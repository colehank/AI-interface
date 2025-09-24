from __future__ import annotations
import os, io, base64, pathlib, sys
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from PIL import Image, ImageOps
from dotenv import load_dotenv
from openai import OpenAI

# ========= 基础工具 =========

def ensure_dir(p: str | pathlib.Path):
    pathlib.Path(p).mkdir(parents=True, exist_ok=True)

def img_to_b64(img: Image.Image) -> str:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")

def b64_to_img(b64: str) -> Image.Image:
    return Image.open(io.BytesIO(base64.b64decode(b64)))

def img_to_data_uri(img: Image.Image) -> str:
    return f"data:image/png;base64,{img_to_b64(img)}"

def load_env_client() -> OpenAI:
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("请先在 .env 里设置 OPENAI_API_KEY", file=sys.stderr)
        sys.exit(1)
    base_url = os.getenv("OPENAI_BASE_URL")
    if base_url:
        return OpenAI(api_key=api_key, base_url=base_url)
    return OpenAI(api_key=api_key)

# ========= 会话与代理 =========

@dataclass
class MessagePart:
    type: str                  # "input_text" | "input_image"
    text: Optional[str] = None # for input_text
    data: Optional[str] = None # for input_image (data URI)

@dataclass
class MultiModalMsg:
    role: str                  # "system" | "user" | "assistant"
    content: List[MessagePart]

@dataclass
class ContextAwareImageAgent:
    client: OpenAI
    response_model: str = "gpt-4o"          # 多模态 + 工具调用
    image_model: str = "gpt-image-1"        # 出图/编辑模型
    default_size: str = "1024x1024"
    history: List[MultiModalMsg] = field(default_factory=list)

    # ---- 历史管理 ----
    def add_text(self, role: str, text: str):
        self.history.append(MultiModalMsg(role=role, content=[MessagePart(type="input_text", text=text)]))

    def add_image(self, role: str, img: Image.Image):
        self.history.append(MultiModalMsg(role=role, content=[MessagePart(type="input_image", data=img_to_data_uri(img))]))

    def get_trimmed_history(self, max_items: int = 6) -> List[Dict[str, Any]]:
        """
        简单裁剪：仅保留最近 max_items 条。真实产品里可按“角色设定/风格板 + 最近2轮 + 关键参考图”更精细裁剪。
        """
        msgs = self.history[-max_items:]
        out: List[Dict[str, Any]] = []
        for m in msgs:
            content = []
            for part in m.content:
                if part.type == "input_text":
                    content.append({"type": "input_text", "text": part.text or ""})
                elif part.type == "input_image":
                    content.append({"type": "input_image", "data": part.data})
            out.append({"role": m.role, "content": content})
        return out

    # ---- Responses + 工具调用 → Images.generate 出图 ----
    def generate_with_context(self, size: Optional[str] = None) -> Image.Image:
        """
        核心：把当前（裁剪后的）历史消息作为多模态 input 传给 Responses，
        强制要求触发 image_generation 工具，然后读取工具参数并自己调用 Images API 出图。
        """
        size = size or self.default_size

        # 1) 触发工具调用（不会直接返回图片）
        resp = self.client.responses.create(
            model=self.response_model,
            input=self.get_trimmed_history(),
            tools=[{"type": "image_generation"}],
            tool_choice="required",
        )

        # 2) 通用化解析 tool_calls（不同 SDK 版本结构略异）
        tool_calls = []
        outputs = getattr(resp, "output", []) or []
        for out in outputs:
            # 有的结构：out.tool_calls
            tc = getattr(out, "tool_calls", None)
            if tc:
                tool_calls.extend(tc)
            # 也可能在 out.content[*].tool_calls
            cnt = getattr(out, "content", None)
            if isinstance(cnt, list):
                for item in cnt:
                    tci = item.get("tool_calls") if isinstance(item, dict) else None
                    if tci:
                        tool_calls.extend(tci)

        if not tool_calls:
            raise RuntimeError("没有拿到 image_generation 的工具调用；请确认模型与 tools 配置。")

        call = next((c for c in tool_calls if str(c.get("type")) == "image_generation"), None)
        if not call:
            raise RuntimeError("未找到 type == 'image_generation' 的工具调用。")

        args = call.get("args") or {}
        prompt = args.get("prompt")
        gen_size = args.get("size", size)
        use_model = args.get("model", self.image_model)

        # 兜底：若工具没填 prompt，就用最近一条 user 文本聚合成 prompt
        if not prompt:
            prompt = self._extract_latest_user_text(default="Generate an image that matches the conversation context.")

        # 3) 真正出图（Images API；b64_json 字段即图片，官方文档说明）  # Docs: image tool + images API
        img_resp = self.client.images.generate(
            model=use_model,
            prompt=prompt,
            size=gen_size,
        )
        b64 = img_resp.data[0].b64_json
        return b64_to_img(b64)

    # ---- 直接编辑上一张图片（可带 mask） ----
    def edit_on_image(self, prompt: str, image: Image.Image, mask: Image.Image | None = None,
                      size: Optional[str] = None) -> Image.Image:
        size = size or self.default_size

        # 官方 Images API 的 edit 会返回 data[0].b64_json  # Docs: images edit response shape
        img_buf = io.BytesIO(); image.save(img_buf, format="PNG"); img_buf.seek(0)
        files = {"image": img_buf}
        if mask:
            mask = ImageOps.expand(mask, border=0)  # 确保为 RGBA/PNG，透明处即编辑区域
            m_buf = io.BytesIO(); mask.save(m_buf, format="PNG"); m_buf.seek(0)
            files["mask"] = m_buf

        r = self.client.images.edit(model=self.image_model, prompt=prompt, size=size, **files)
        return b64_to_img(r.data[0].b64_json)

    # ---- 小工具：抓最近一条 user 文本 ----
    def _extract_latest_user_text(self, default: str = "") -> str:
        for m in reversed(self.history):
            if m.role == "user":
                for part in reversed(m.content):
                    if part.type == "input_text" and part.text:
                        return part.text
        return default


# ========= 测试用例 =========

def main():
    client = load_env_client()
    agent = ContextAwareImageAgent(client=client)

    out_dir = pathlib.Path("out_images"); ensure_dir(out_dir)

    # 1) 先放“设定/世界观/角色卡”（system & user）
    agent.add_text("system", "You are a helpful visual assistant. Follow style and character continuity.")
    agent.add_text("user", "主角：黑发女侦探，风衣，赛博朋克风；请牢记她的脸部特征与服饰。")

    # 2) 第一次生成：用户提出详细需求
    agent.add_text("user", "生成一张她在霓虹雨夜街头的半身照，电影感，侧光。")
    img1 = agent.generate_with_context(size="768x1024")
    img1_path = out_dir / "case1_first_gen.png"; img1.save(img1_path)
    print(f"[OK] 首次生成：{img1_path}")

    # 将第一次的图像作为“上下文参考图”喂回去（assistant 一侧贴图，有助于连续性）
    agent.add_image("assistant", img1)

    # 3) 第二次生成：继续参考上一张（上下文感知）
    agent.add_text("user", "保持同一角色与服饰，这次在室内仓库，冷色调顶光，给我一个近景特写。")
    img2 = agent.generate_with_context(size="768x1024")
    img2_path = out_dir / "case2_ctx_continuation.png"; img2.save(img2_path)
    print(f"[OK] 连续生成（参考上一张）：{img2_path}")

    # 4) 图像编辑：在上一张图基础上做小改（比如加一点霓虹反光）
    edit_prompt = "在不改变人物五官与服饰的基础上，增加霓虹灯反光与雨滴质感，赛博朋克氛围更强。"
    img2_edit = agent.edit_on_image(prompt=edit_prompt, image=img2, mask=None, size="768x1024")
    img2e_path = out_dir / "case3_edit_on_prev.png"; img2_edit.save(img2e_path)
    print(f"[OK] 编辑上一张：{img2e_path}")

    print("全部完成。打开 out_images/ 查看效果。")

if __name__ == "__main__":
    main()