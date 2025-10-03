# %%
from __future__ import annotations

import base64
import io
import json
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Optional, Tuple, Union
from collections.abc import Iterable

from dotenv import load_dotenv
from openai import OpenAI
from PIL import Image

load_dotenv()


JsonMode = Literal["text", "json"]
Role = Literal["system", "user", "assistant"]
# %%
@dataclass
class Part:
    """
    单个内容块：文本或图片
    - 文本：{"type": "input_text", "text": "..."}
    - 图片：{"type": "input_image", "image_url": "data:image/png;base64,...."}
      或（可选 detail） {"type":"input_image","image_url":{"url": "...", "detail": "low|high"}}
    """
    type: Literal["input_text", "input_image"]
    text: str | None = None
    image_url: str | dict[str, Any] | None = None

    def to_payload(self) -> dict[str, Any]:
        if self.type == "input_text":
            if not isinstance(self.text, str):
                raise ValueError("input_text part requires 'text' (str).")
            return {"type": "input_text", "text": self.text}
        elif self.type == "input_image":
            if not self.image_url:
                raise ValueError("input_image part requires 'image_url'.")
            return {"type": "input_image", "image_url": self.image_url}
        elif self.type == "output_text":
            if not isinstance(self.text, str):
                raise ValueError("output_text part requires 'text' (str).")
            return {"type": "output_text", "text": self.text}
        else:
            raise ValueError(f"Unsupported part type: {self.type}")


@dataclass
class Message:
    role: Role
    content: list[Part]

    def to_payload(self) -> dict[str, Any]:
        return {
            "role": self.role,
            "content": [p.to_payload() for p in self.content],
        }


def _infer_mime_from_pil(img: Image.Image) -> str:
    """
    优先使用 Image.format，如果缺失则回退 PNG；并映射到标准 mime。
    """
    fmt = (img.format or "PNG").upper()
    if fmt == "JPEG" or fmt == "JPG":
        return "image/jpeg"
    if fmt == "PNG":
        return "image/png"
    if fmt == "WEBP":
        return "image/webp"
    if fmt == "GIF":
        return "image/gif"
    if fmt == "BMP":
        return "image/bmp"
    if fmt == "TIFF" or fmt == "TIF":
        return "image/tiff"
    # 回退：根据 PIL 不确定时，统一选择 PNG
    return "image/png"


def _pil_to_data_uri(
    img: Image.Image,
    *,
    max_side: int = 2048,
    prefer_webp: bool = True,
    webp_quality: int = 85,
) -> tuple[str, int]:
    """
    将 PIL.Image.Image 转 Data URI（base64）
    - 约束：将最长边压到 max_side（控制 payload 体积，降低延迟/费用）
    - 优先 WEBP（多数场景体积更小），否则使用原生/PNG
    返回：(data_uri, bytes_size)
    """
    # 尺寸压缩（最长边不超过 max_side）
    w, h = img.size
    scale = min(1.0, float(max_side) / max(w, h))
    if scale < 1.0:
        new_w, new_h = int(w * scale), int(h * scale)
        img = img.resize((new_w, new_h), Image.LANCZOS)

    # 选择编码格式
    mime = _infer_mime_from_pil(img)
    out = io.BytesIO()
    if prefer_webp:
        mime = "image/webp"
        img.save(out, format="WEBP", quality=webp_quality, method=6)
    else:
        # 保持原生（若不可靠，回退 PNG）
        fmt = (img.format or "").upper()
        if fmt in {"JPEG", "JPG"}:
            mime = "image/jpeg"
            img.save(out, format="JPEG", quality=90, optimize=True)
        elif fmt == "PNG":
            mime = "image/png"
            img.save(out, format="PNG", optimize=True)
        else:
            mime = "image/png"
            img.save(out, format="PNG", optimize=True)

    binary = out.getvalue()
    b64 = base64.b64encode(binary).decode("ascii")
    data_uri = f"data:{mime};base64,{b64}"
    return data_uri, len(binary)

@dataclass
class AgentLLM:
    """
    使用 OpenAI Responses API 的通用 Agent 封装
    - 支持文字 + 图片（PIL.Image.Image）输入
    - 支持文本/严格 JSON 输出
    - 维护对话历史（可选）
    """
    api_key: str | None = None
    base_url: str | None = None
    model: str = "gpt-5-nano"
    client: OpenAI = field(init=False)
    history: list[Message] = field(default_factory=list)

    def __post_init__(self):
        self.client = OpenAI(
            api_key=self.api_key or os.getenv("OPENAI_API_KEY"),
            base_url=self.base_url or os.getenv("OPENAI_BASE_URL"),
        )

    # ------------- 对外主方法 -------------

    def clear_history(self) -> None:
        self.history.clear()

    def add_system_prompt(self, text: str) -> None:
        self.history.append(
            Message(role="system", content=[Part(type="input_text", text=text)])
        )

    def add_user_text(self, text: str) -> None:
        self.history.append(
            Message(role="user", content=[Part(type="input_text", text=text)])
        )
        
    def add_assistant_text(self, text: str) -> None:
        self.history.append(
            Message(role="assistant", content=[Part(type="output_text", text=text)])
        )

    def add_user_image(
        self,
        image: Image.Image,
        *,
        detail: Literal["auto", "low", "high"] = "auto",
        prefer_webp: bool = True,
        max_side: int = 2048,
    ) -> None:
        """
        将 PIL 图片加入为用户消息的一部分；如果历史最后一条是 user，就合并到同一条里。
        """
        data_uri, _ = _pil_to_data_uri(image, max_side=max_side, prefer_webp=prefer_webp)

        image_url: str | dict[str, Any]
        if detail == "auto":
            image_url = data_uri
        else:
            # 文档允许在 image_url 使用对象形式附带 detail（低/高分辨率分析）：
            # {"url": "data:...base64,...", "detail": "low|high"}
            image_url = {"url": data_uri, "detail": detail}

        if self.history and self.history[-1].role == "user":
            self.history[-1].content.append(Part(type="input_image", image_url=image_url))
        else:
            self.history.append(Message(role="user", content=[Part(type="input_image", image_url=image_url)]))

    def call(
        self,
        *,
        response_format: JsonMode = "text",
        max_output_tokens: int | None = None,
        temperature: float | None = None,
        top_p: float | None = None,
        seed: int | None = None,
        json_schema: dict[str, Any] | None = None,
        # 兼容一次性快速调用：传入额外的当前用户文本/图片（不会写入历史）
        transient_user_text: str | None = None,
        transient_user_images: list[Image.Image] | None = None,
    ) -> str | dict[str, Any]:
        """
        执行一次对话：
        - response_format="text"：返回字符串
        - response_format="json"：严格 JSON；如提供 json_schema，会走结构化输出（强约束）
        """
        if not self.history and not (transient_user_text or transient_user_images):
            raise ValueError("No input provided. Add messages or use transient_user_* arguments.")

        # 构造 input（历史 + 本次临时输入）
        inputs: list[dict[str, Any]] = [m.to_payload() for m in self.history]

        if transient_user_text or transient_user_images:
            parts: list[Part] = []
            if transient_user_text:
                parts.append(Part(type="input_text", text=transient_user_text))
            for img in transient_user_images or []:
                data_uri, _ = _pil_to_data_uri(img)
                parts.append(Part(type="input_image", image_url=data_uri))
            inputs.append(Message(role="user", content=parts).to_payload())

        # 组装请求参数
        params: dict[str, Any] = {
            "model": self.model,
            "input": inputs,
        }

        if max_output_tokens is not None:
            params["max_output_tokens"] = max_output_tokens
        if temperature is not None:
            params["temperature"] = temperature
        if top_p is not None:
            params["top_p"] = top_p
        if seed is not None:
            params["seed"] = seed

        # 严格 JSON 输出：Responses API 支持结构化输出（提供 JSON Schema）
        # 若仅要求 JSON 但不提供 schema，也可使用 {"type":"json_object"} 作为宽松 JSON。
        if response_format == "json":
            if json_schema:
                params["response_format"] = {
                    "type": "json_schema",
                    "json_schema": {
                        "name": "response",
                        "schema": json_schema,
                        "strict": True,
                    },
                }
            else:
                params["response_format"] = {"type": "json_object"}

        # 发送请求
        resp = self.client.responses.create(**params)

        # 解析输出
        # Responses API 的主内容通常位于 resp.output_text（SDK便捷属性）或 resp.output[...]
        text = getattr(resp, "output_text", None)
        if text is None:
            # 回退策略：尝试从内容块提取
            try:
                # 新 SDK 通常有 .output 结构化块
                chunks = getattr(resp, "output", None)
                if chunks and isinstance(chunks, list):
                    # 寻找第一个 text 类型返回
                    for ch in chunks:
                        if isinstance(ch, dict):
                            if ch.get("type") in ("message", "output_text"):
                                candidate = ch.get("content") or ch.get("text")
                                if isinstance(candidate, str):
                                    text = candidate
                                    break
                            # 其他结构（如 tool calls）不在此示例解析范围
                if text is None:
                    # 最后兜底：从 choices(旧结构) 或 raw 字段推断
                    text = json.dumps(resp.dict())  # 不建议，但至少不抛异常
            except Exception:
                text = json.dumps(resp.dict())

        if response_format == "json":
            # 尝试解析 JSON
            try:
                return json.loads(text)
            except Exception as e:
                # 如果你要求严格 JSON，但模型未遵守，可以抛错帮助定位
                raise ValueError(f"Expected JSON but got non-JSON text: {text[:2000]}") from e
        else:
            return text

    # ------------- 便捷一次性方法 -------------

    def ask_text(
        self,
        prompt: str,
        *,
        response_format: JsonMode = "text",
        **kwargs: Any,
    ) -> str | dict[str, Any]:
        """
        快速一次性调用：只发一条用户文本，不写入历史。
        """
        return self.call(
            response_format=response_format,
            transient_user_text=prompt,
            **kwargs,
        )

    def chat(
        self,
        user_text: str | None = None,
        user_images: list[Image.Image] | None = None,
        assistant_text: str | None = None,
        *,
        response_format: JsonMode = "text",
        **kwargs: Any,
    ) -> str | dict[str, Any]:
        """
        将传入内容**写入历史**并调用。
        """
        if user_text:
            self.add_user_text(user_text)
        if assistant_text:
            self.add_assistant_text(assistant_text)
        for img in user_images or []:
            self.add_user_image(img)
        response = self.call(response_format=response_format, **kwargs)
        if isinstance(response, str) and assistant_text is None:
            self.add_assistant_text(response)
        return response

#%%
if __name__ == "__main__":
    agent = AgentLLM()
    img = Image.new('RGB', (100, 100), color='green')
    agent.add_system_prompt("你是一个视觉识别专家。")
    agent.add_user_text("这张图片是什么颜色？")
    agent.add_system_prompt("你是一个视觉识别专家。")
    agent.add_user_image(img)
# %%
    res = agent.call()
    agent.add_assistant_text(res)
    agent.chat(
        user_text="重复一下你刚刚的回答",
    )
    agent.history
#%%
