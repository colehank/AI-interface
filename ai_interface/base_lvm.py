# %%
from __future__ import annotations

import base64
import io
import os
from typing import Any
from typing import Dict
from typing import Optional

from dotenv import load_dotenv
from openai import OpenAI
from PIL import Image
load_dotenv()
from wasabi import msg as wmsg
# %%
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
        b64_str = response.data[0].b64_json
        img_data = base64.b64decode(b64_str)
        image = Image.open(io.BytesIO(img_data))
        return image

    def edit(
        self,
        image: Image.Image,
        prompt: str,
        mask: Image.Image | None = None,
        model: str = 'gpt-image-1',
        size: str = '1024x1024',
    ) -> Image.Image:
        """
        Edit an existing image with a prompt and optional mask.

        The image and mask (if provided) are sent as file-like objects.
        Returns the first edited image as a PIL Image.
        """
        # Prepare image file
        img_buf = io.BytesIO()
        image.save(img_buf, format='PNG')
        img_buf.seek(0)

        # Prepare mask file if provided
        files: dict[str, Any] = {'image': img_buf}
        if mask:
            mask_buf = io.BytesIO()
            mask.save(mask_buf, format='PNG')
            mask_buf.seek(0)
            files['mask'] = mask_buf

        response = self.client.images.edit(
            model=model,
            prompt=prompt,
            size=size,
            **files,
        )
        edited_b64 = response.data[0].b64_json
        edited_img = Image.open(io.BytesIO(base64.b64decode(edited_b64)))
        return edited_img

class AgentLVM():
    def __init__(self, api_key: str | None = None, base_url: str | None = None):
        """
        初始化 Agent LVM 客户端

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

    def _encode_img(self, image: Image.Image) -> str:
        img_buf = io.BytesIO()
        image.save(img_buf, format='PNG')
        img_buf.seek(0)
        return base64.b64encode(img_buf.read()).decode('utf-8')

    def _decode_img(self, img_b64: str) -> Image.Image:
        img_data = base64.b64decode(img_b64)
        return Image.open(io.BytesIO(img_data))

    def create(
        self,
        msg: list[dict],
        model: str = 'gpt-4o',
    ) -> Image.Image:

        response = self.client.responses.create(
            model=model,
            input=msg,
            tools=[{'type': 'image_generation'}],
            tool_choice='required',
        )
        image_generation_calls = [
            output
            for output in response.output
            if output.type == 'image_generation_call'
        ]
        image_data = [output.result for output in image_generation_calls]

        if image_data:
            image_base64 = image_data[0]
            img_data = base64.b64decode(image_base64)
            image = Image.open(io.BytesIO(img_data))
            return image
        else:
            raise ValueError(response.output.content)

    def edit(
        self,
        prompt: str,
        image: Image.Image | list[Image.Image],
        model: str = 'gpt-4o',
    ) -> Image.Image:
        """
        Edit an existing image with a prompt.

        The image is sent as a file-like object.
        Returns the first edited image as a PIL Image.
        """
        if isinstance(image, Image.Image):
            image = [image]
        b64_images = [self._encode_img(img) for img in image]
        input = [
            {
                'role': 'user',
                'content': [
                    {'type': 'input_text', 'text': prompt},
                ],
            },
        ]
        for img_b64 in b64_images:
            input[0]['content'].append(
                {'type': 'input_image', 'data': f"data:image/png;base64,{img_b64}"},
            )
        response = self.client.responses.create(
            model=model,
            input=input,
            tools=[{'type': 'image_generation'}],
            tool_choice='required',
        )
        image_generation_calls = [
            output
            for output in response.output
            if output.type == 'image_generation_call'
        ]
        image_data = [output.result for output in image_generation_calls]
        if image_data:
            image_base64 = image_data[0]
            img_data = base64.b64decode(image_base64)
            image = Image.open(io.BytesIO(img_data))
            return image
        else:
            raise ValueError(response.output.content)
#%%
if __name__ == '__main__':
    vlm = BaseLVM()
    res = vlm.create('A beautiful landscape with mountains and a river')
    #%%
    vlm = BaseLVM()
    res = vlm.edit(res, 'Add a rainbow in the sky')
    #%%
    a_lvm = AgentLVM()
    res = a_lvm.create(
        msg=[
            {'role':'system','content':'You are a helpful assistant that generates images.'},
            {'role':'user','content':'Generate an image of a futuristic city.'},
        ],
    )
    #%%
    character_ref = Image.open('/Users/zgh/Desktop/workingdir/AI-interface/ai_interface/datasets/lvm_prompts/character_ref.png')
    a_lvm = AgentLVM()
    res = a_lvm.edit(
        image=character_ref,
        prompt='Make the character look more futuristic with neon lights and a cyberpunk style.',
    )
#%%
