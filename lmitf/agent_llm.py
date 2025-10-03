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
    type: Literal["input_text", "input_image", "output_text"]
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


def _make_text_part(role: Role, text: str) -> Part:
    if not isinstance(text, str):
        raise TypeError("Text content must be a string.")
    part_type: Literal["input_text", "output_text"]
    part_type = "output_text" if role == "assistant" else "input_text"
    return Part(type=part_type, text=text)


def _make_image_part(
    image: Image.Image,
    *,
    detail: Literal["auto", "low", "high"] = "auto",
    prefer_webp: bool = True,
    max_side: int = 2048,
) -> Part:
    if not isinstance(image, Image.Image):
        raise TypeError("Image content must be a PIL.Image.Image instance.")
    data_uri, _ = _pil_to_data_uri(image, max_side=max_side, prefer_webp=prefer_webp)
    image_url: str | dict[str, Any]
    if detail == "auto":
        image_url = data_uri
    else:
        image_url = {"url": data_uri, "detail": detail}
    return Part(type="input_image", image_url=image_url)


def _image_parts_from_value(
    image_value: Any,
    *,
    detail: Literal["auto", "low", "high"] = "auto",
    prefer_webp: bool = True,
    max_side: int = 2048,
) -> list[Part]:
    if isinstance(image_value, Image.Image):
        return [_make_image_part(image_value, detail=detail, prefer_webp=prefer_webp, max_side=max_side)]
    if isinstance(image_value, dict):
        nested_detail = image_value.get("detail", detail)
        nested_prefer_webp = image_value.get("prefer_webp", prefer_webp)
        nested_max_side = image_value.get("max_side", max_side)
        if "image" in image_value:
            return _image_parts_from_value(
                image_value["image"],
                detail=nested_detail,
                prefer_webp=nested_prefer_webp,
                max_side=nested_max_side,
            )
    raise TypeError("Unsupported image payload; expected PIL.Image.Image or configuration dict containing 'image'.")


def _parts_from_value(role: Role, value: Any) -> list[Part]:
    if value is None:
        return []
    if isinstance(value, Part):
        return [Part(type=value.type, text=value.text, image_url=value.image_url)]
    if isinstance(value, Message):
        if value.role != role:
            raise ValueError(f"Role mismatch: expected {role}, got {value.role}.")
        return [Part(type=p.type, text=p.text, image_url=p.image_url) for p in value.content]
    if isinstance(value, str):
        return [_make_text_part(role, value)]
    if isinstance(value, Image.Image):
        return _image_parts_from_value(value)
    if isinstance(value, (list, tuple)):
        parts: list[Part] = []
        for item in value:
            parts.extend(_parts_from_value(role, item))
        return parts
    if isinstance(value, dict):
        if "type" in value:
            part_type = value.get("type")
            if part_type == "input_text":
                text = value.get("text")
                if not isinstance(text, str):
                    raise ValueError("input_text part requires 'text'.")
                return [Part(type="input_text", text=text)]
            if part_type == "output_text":
                text = value.get("text")
                if not isinstance(text, str):
                    raise ValueError("output_text part requires 'text'.")
                return [Part(type="output_text", text=text)]
            if part_type == "input_image":
                image_url = value.get("image_url")
                if image_url is None:
                    raise ValueError("input_image part requires 'image_url'.")
                return [Part(type="input_image", image_url=image_url)]
        parts: list[Part] = []
        if "text" in value:
            parts.extend(_parts_from_value(role, value["text"]))
        image_kwargs = {
            "detail": value.get("detail", "auto"),
            "prefer_webp": value.get("prefer_webp", True),
            "max_side": value.get("max_side", 2048),
        }
        if "image" in value and value["image"] is not None:
            parts.extend(_image_parts_from_value(value["image"], **image_kwargs))
        if "images" in value and value["images"] is not None:
            images_value = value["images"]
            if not isinstance(images_value, (list, tuple)):
                raise TypeError("'images' must be a list or tuple of PIL.Image.Image instances.")
            for image_item in images_value:
                parts.extend(_image_parts_from_value(image_item, **image_kwargs))
        if "content" in value and value["content"] is not None:
            parts.extend(_parts_from_value(role, value["content"]))
        if parts:
            return parts
        raise ValueError("Dictionary message value must include 'text', 'image', 'images', or 'content'.")
    raise TypeError(f"Unsupported message payload type for role '{role}': {type(value)!r}")


def _build_messages_from_dict(message: dict[str, Any]) -> list[Message]:
    if not isinstance(message, dict):
        raise TypeError("message must be a dict mapping roles to payloads.")
    messages: list[Message] = []
    for role_key, value in message.items():
        if role_key not in {"system", "user", "assistant"}:
            raise ValueError(f"Unsupported role '{role_key}'. Expected 'system', 'user', or 'assistant'.")
        parts = _parts_from_value(role_key, value)
        if parts:
            messages.append(Message(role=role_key, content=parts))
    if not messages:
        raise ValueError("message must contain at least one non-empty role entry.")
    return messages

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
    model: str = "gpt-4.1-mini"  # 你可以换为适配视觉的最新模型，如 gpt-4o-mini / gpt-4.1
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
        part = _make_image_part(
            image,
            detail=detail,
            prefer_webp=prefer_webp,
            max_side=max_side,
        )
        if self.history and self.history[-1].role == "user":
            self.history[-1].content.append(part)
        else:
            self.history.append(Message(role="user", content=[part]))

    def call(
        self,
        message: dict[str, Any],
        *,
        response_format: JsonMode = "text",
        max_output_tokens: int | None = None,
        temperature: float | None = None,
        top_p: float | None = None,
        seed: int | None = None,
        json_schema: dict[str, Any] | None = None,
    ) -> str | dict[str, Any]:
        """
        执行一次对话，仅基于传入的 message 字典构建输入：
        - message: {"system": ..., "user": ..., "assistant": ...}
        - response_format="text"：返回字符串
        - response_format="json"：严格 JSON；如提供 json_schema，会走结构化输出（强约束）
        """
        messages = _build_messages_from_dict(message)
        return self._call_with_messages(
            messages,
            response_format=response_format,
            max_output_tokens=max_output_tokens,
            temperature=temperature,
            top_p=top_p,
            seed=seed,
            json_schema=json_schema,
        )

    def _call_with_messages(
        self,
        messages: list[Message],
        *,
        response_format: JsonMode = "text",
        max_output_tokens: int | None = None,
        temperature: float | None = None,
        top_p: float | None = None,
        seed: int | None = None,
        json_schema: dict[str, Any] | None = None,
    ) -> str | dict[str, Any]:
        inputs: list[dict[str, Any]] = [m.to_payload() for m in messages]

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

        resp = self.client.responses.create(**params)

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
        message: dict[str, Any] = {"user": prompt}
        return self.call(
            message,
            response_format=response_format,
            **kwargs,
        )

    def chat(
        self,
        message: dict[str, Any],
        *,
        response_format: JsonMode = "text",
        persist_history: bool = True,
        **kwargs: Any,
    ) -> str | dict[str, Any]:
        """
        基于 message 执行一次对话，可选择是否写入历史。
        """
        messages = _build_messages_from_dict(message)
        response = self._call_with_messages(
            messages,
            response_format=response_format,
            **kwargs,
        )
        if persist_history:
            self.history.extend(messages)
            if isinstance(response, str):
                self.history.append(
                    Message(role="assistant", content=[Part(type="output_text", text=response)])
                )
            elif isinstance(response, dict):
                self.history.append(
                    Message(
                        role="assistant",
                        content=[
                            Part(
                                type="output_text",
                                text=json.dumps(response, ensure_ascii=False),
                            )
                        ],
                    )
                )
        return response

#%%
agent = AgentLLM()
img = Image.new('RGB', (100, 100), color='green')
res = agent.call(
    {
        "system": "你是一个颜色识别专家。",
        "user": [
            "请告诉我这是什么颜色？",
            img,
        ],
    },
    response_format='json',
)
print(res)
#%%
res = agent.chat(
    {
        "system": "你是一个颜色识别专家。",
        "user": "再告诉我一次这是什么颜色？",
    },
    response_format='text',
)

#%%
