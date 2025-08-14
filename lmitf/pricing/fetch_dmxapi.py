import json
import re
import typing as t
from dataclasses import dataclass
from urllib.parse import urlparse
import requests
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()
_HTML_TAG_RE = re.compile(r"<[^>]+>")
# 常见 emoji & pictograph 范围（尽量覆盖，防止说明里花里胡哨的符号）
_EMOJI_RE = re.compile(
    "["                     # 一些常见 emoji block
    "\U0001F300-\U0001FAFF" # Misc Symbols and Pictographs, Supplemental Symbols
    "\U00002700-\U000027BF" # Dingbats
    "\U00002600-\U000026FF" # Misc Symbols
    "\U0001F900-\U0001F9FF" # Supplemental Symbols and Pictographs
    "]+",
    flags=re.UNICODE
)


def _strip_html_and_emoji(text: str) -> str:
    if not text:
        return ""
    text = _HTML_TAG_RE.sub("", text)
    text = _EMOJI_RE.sub("", text)
    # 压缩多余空白
    text = re.sub(r"\s+", " ", text).strip()
    return text


@dataclass
class ModelPrice:
    billing_type: str                   # 'token' 或 'per_call'
    input_per_m: t.Optional[float]  # 每百万 tokens（人民币）
    output_per_m: t.Optional[float] # 每百万 tokens（人民币）
    per_call: t.Optional[float]     # 按次（人民币）


class DMXPricing:
    """
    从 DMXAPI 的 /api/pricing 构建价格表。

    约定与页面一致：
      - 输入价 = 4 * base_price
      - 输出价 = 4 * base_price * completion_ratio
      - 按次计费（isPrice == True）使用 per_call_price，单位“元/次”，不再计算 tokens 价
    说明与名字清洗：
      - 模型名称使用 key（不带 emoji/宣传）
      - 说明字段做 HTML/emoji 清洗
    """

    TOKEN_MULTIPLIER = 2.0  # 关键：页面展示为 4 * base_price（输入），输出再乘 completion_ratio

    def __init__(self, pricing_url: str, timeout: float = 15.0):
        self.pricing_url = self._normalize_to_api(pricing_url)
        self.timeout = timeout

        data = self._fetch_json(self.pricing_url)
        if "data" not in data:
            raise ValueError("pricing 接口返回缺少 data 字段")

        self._raw = data["data"]

        # 解析结构
        # model_info 是 JSON 字符串（列表），内部形如 [ [model_key, {detail...}], ... ]
        raw_model_info = self._raw.get("model_info")
        if isinstance(raw_model_info, str):
            model_info_list = json.loads(raw_model_info)
        elif isinstance(raw_model_info, list):
            model_info_list = raw_model_info
        else:
            model_info_list = []

        # 模型 -> 厂商/标签/说明
        self._model_meta = {}
        for entry in model_info_list:
            # entry: [key, { ..detail.. }]
            if not isinstance(entry, list) or len(entry) != 2:
                continue
            key, detail = entry
            if not isinstance(key, str) or not isinstance(detail, dict):
                continue
            supplier = detail.get("supplier", "") or ""
            tags = detail.get("tags") or []
            if isinstance(tags, list):
                tags_str = "、".join([str(x) for x in tags if x is not None])
            else:
                tags_str = str(tags)
            illustrate = _strip_html_and_emoji(detail.get("illustrate", "") or "")
            self._model_meta[key] = {
                "supplier": supplier,
                "tags": tags_str,
                "illustrate": illustrate,
            }

        # 分组与价格：一般只有 'default'
        model_group = self._raw.get("model_group") or {}
        if not model_group:
            raise ValueError("未找到 model_group 数据")
        # 取第一个分组名称
        self.group_name = next(iter(model_group.keys()))
        group_obj = model_group[self.group_name]
        self.group_ratio = float(group_obj.get("GroupRatio", 1) or 1)
        self._group_model_price = group_obj.get("ModelPrice") or {}

        # 补全倍率
        self._completion_ratio = self._raw.get("model_completion_ratio") or {}

        # 构建 DataFrame
        self.df = self._build_df()

    # ---------- 公共 API ----------

    def get_model_price(self, model_key: str) -> ModelPrice:
        """
        根据模型名称（key）返回 ModelPrice
        """
        r = self._calc_price_for_model(model_key)
        if r is None:
            raise KeyError(f"未找到模型或价格信息：{model_key}")
        return r

    def get_models_by_vendor(self, vendor_key: str) -> pd.DataFrame:
        """
        根据厂商（supplier）筛选所有模型（返回 df 的一个子集）
        """
        return self.df[self.df["模型厂商"] == vendor_key].copy()

    # ---------- 内部实现 ----------

    def _normalize_to_api(self, url: str) -> str:
        """
        允许传入 /pricing 页面地址，自动转为 /api/pricing
        """
        u = urlparse(url)
        if u.netloc and u.path == "/pricing":
            return f"{u.scheme}://{u.netloc}/api/pricing"
        if u.netloc and u.path == "/api/pricing":
            return url
        # 没有 host 的话，直接原样返回（交给 requests 报错）
        return url

    def _fetch_json(self, url: str) -> dict:
        headers = {
            "User-Agent": "Mozilla/5.0 (DMXPricing; +https://github.com)",
            "Accept": "application/json,text/plain,*/*",
            "Referer": url.replace("/api/pricing", "/pricing"),
        }
        resp = requests.get(url, headers=headers, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()

    def _get_base_price_entry(self, model_key: str) -> t.Optional[dict]:
        """
        从 group 的 ModelPrice 中取到一个模型的价格条目：
        形如 {'isPrice': bool, 'price': number}
        """
        return self._group_model_price.get(model_key)

    def _get_completion_ratio(self, model_key: str) -> float:
        v = self._completion_ratio.get(model_key)
        try:
            return float(v)
        except Exception:
            return 1.0

    def _calc_price_for_model(self, model_key: str) -> t.Optional[ModelPrice]:
        """
        计算一个模型的价格（匹配网页展示）
        """
        entry = self._get_base_price_entry(model_key)
        if entry is None:
            return None

        is_per_call = bool(entry.get("isPrice"))
        base_price = float(entry.get("price", 0.0) or 0.0)

        if is_per_call:
            # /次，不做 token 价格
            return ModelPrice(
                billing_type="per_call",
                input_per_m=None,
                output_per_m=None,
                per_call=base_price * self.group_ratio,  # 分组倍率仍叠加
            )

        # token 计费：页面展示规则
        comp_ratio = self._get_completion_ratio(model_key)  # 补全倍率
        input_price = self.TOKEN_MULTIPLIER * base_price * self.group_ratio
        output_price = input_price * comp_ratio

        return ModelPrice(
            billing_type="token",
            input_per_m=round(input_price, 6),
            output_per_m=round(output_price, 6),
            per_call=None,
        )

    def _build_df(self) -> pd.DataFrame:
        rows = []
        for model_key in self._group_model_price.keys():
            meta = self._model_meta.get(model_key, {})
            price = self._calc_price_for_model(model_key)

            supplier = meta.get("supplier", "")
            tags = meta.get("tags", "")
            illustrate = meta.get("illustrate", "")

            if price is None:
                # 没有价格配置（极少数），占位
                rows.append({
                    "模型厂商": supplier,
                    "模型名称": model_key,              # 使用 key（干净、不带 emoji/宣传）
                    "标签": tags,
                    "计费类型": "unknown",
                    "人民币计费价格（输入tokens/百万）": None,
                    "人民币计费价格（输出tokens/百万）": None,
                    "人民币计费价格（按次）": None,
                    "分组": self.group_name,
                    "说明": illustrate,
                })
                continue

            if price.billing_type == "per_call":
                rows.append({
                    "模型厂商": supplier,
                    "模型名称": model_key,
                    "标签": tags,
                    "计费类型": "按次",
                    "人民币计费价格（输入tokens/百万）": None,
                    "人民币计费价格（输出tokens/百万）": None,
                    "人民币计费价格（按次）": price.per_call,
                    "分组": self.group_name,
                    "说明": illustrate,
                })
            else:
                rows.append({
                    "模型厂商": supplier,
                    "模型名称": model_key,
                    "标签": tags,
                    "计费类型": "按tokens",
                    "人民币计费价格（输入tokens/百万）": price.input_per_m,
                    "人民币计费价格（输出tokens/百万）": price.output_per_m,
                    "人民币计费价格（按次）": None,
                    "分组": self.group_name,
                    "说明": illustrate,
                })

        df = pd.DataFrame(rows)
        # 为一致性，按厂商+模型名称排序
        if not df.empty:
            df.sort_values(["模型厂商", "模型名称"], inplace=True, kind="mergesort")
            df.reset_index(drop=True, inplace=True)
        return df

    def fetch_balance(self, api_key=None, user_id=None):
        """
        Fetch DMX balance using API key and user ID.

        Args:
            api_key (str): API key, defaults to OPENAI_API_KEY environment variable
            user_id (str): User ID, defaults to '3804'

        Returns:
            dict: Balance data from API response
        """
        if api_key is None:
            api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("API key is required. Please set the OPENAI_API_KEY environment variable.")
            return {}
        if user_id is None:
            user_id = '3804'

        url = f"https://www.dmxapi.cn/api/token/key/{api_key}"

        headers = {
            "Accept": "application/json",
            "Rix-Api-User": user_id,
        }

        response = requests.request("GET", url, headers=headers)
        try:
            response_data = response.json()['data']
        except (json.JSONDecodeError, KeyError):
            print("Error fetching balance data. Please check your API key and user ID.")
            print("Response content:", response.text)
            return {}
        remaining_balance = response_data['remain_quota'] / 500000
        print(f"API Key User {response_data['name']} remaining {remaining_balance}¥")
        return remaining_balance

def fetch_price(
    url: str,
    model: str
    ) -> dict[str:float]:
    client = DMXPricing(url)
    price = client.get_model_price(model)
    return price.__dict__

def fetch_all(
    url: str
    ) -> pd.DataFrame:
    client = DMXPricing(url)
    return client.df

def fetch_model_from_supplier(
    url: str,
    supplier: str
    ) -> list:
    client = DMXPricing(url)
    models = client.get_models_by_vendor(supplier)
    return models['模型名称'].tolist()

# ---------------------------
# 简单用法示例（你可以在其它文件里导入使用）：
if __name__ == "__main__":
    url = "https://www.dmxapi.cn/pricing"
    client = DMXPricing(url)


