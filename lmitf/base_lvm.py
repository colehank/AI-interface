# %%
from __future__ import annotations

import base64
import io
import os

from dotenv import load_dotenv
from openai import OpenAI
from PIL import Image
from .utils import buf_image, res_to_image
load_dotenv()

class BaseLVM:
    """
    OpenAI LVM (Language Vision Model) 客户端封装类

    提供对 OpenAI Vision API 的简化访问接口，支持图像处理和文本生成。
    自动处理环境变量配置，维护调用历史记录。

    Attributes
    ----------
    client : openai.Image
        OpenAI 图像处理客户端实例
    call_history : list[str | dict[str, Any]]
        API 调用响应的历史记录
    """

    def __init__(self, api_key: str | None = None, base_url: str | None = None):
        """
        初始化 VLM 客户端

        Parameters
        ----------
        api_key : str, optional
            OpenAI API 密钥。如果未提供，将从环境变量 OPENAI_API_KEY 读取
        base_url : str, optional
            API 基础URL。如果未提供，将从环境变量 OPENAI_BASE_URL 读取
        """
        self.client = OpenAI(
            api_key=api_key or os.getenv('OPENAI_API_KEY'),
            base_url=base_url or os.getenv('OPENAI_BASE_URL'),
        )

    def create(
        self,
        prompt: str,
        model: str = 'gpt-image-1',
        size: str = '1024x1024',
    )-> Image.Image:

        response = self.client.images.generate(
            model=model,
            prompt=prompt,
            size=size,
        )
        return res_to_image(response)

    def edit(
        self,
        image: Image.Image | list[Image.Image],
        prompt: str,
        model: str = 'gpt-image-1',
        size: str = '1024x1024',
        input_fidelity:str = 'low',
    ) -> Image.Image:
        """
        Edit an existing image with a prompt and optional mask.

        The image and mask (if provided) are sent as file-like objects.
        Returns the first edited image as a PIL Image.
        """
        # Prepare image file
        imgs = [
            buf_image(img) if isinstance(img, Image.Image) else img
            for img in (image if isinstance(image, list) else [image])
        ]

        response = self.client.images.edit(
            model=model,
            prompt=prompt,
            size=size,
            image=imgs,
            input_fidelity=input_fidelity,
        )
        return res_to_image(response)