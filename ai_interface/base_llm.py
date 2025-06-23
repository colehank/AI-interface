from __future__ import annotations

import json
import os
import re
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from dotenv import load_dotenv
from openai import OpenAI

from .utils import print_conversation
load_dotenv()


class BaseLLM:
    """
    OpenAI LLM 客户端封装类

    提供对 OpenAI Chat Completions API 的简化访问接口，支持文本和 JSON 格式响应。
    自动处理环境变量配置，维护调用历史记录。

    Attributes
    ----------
    client : OpenAI
        OpenAI 客户端实例
    call_history : List[Union[str, Dict[str, Any]]]
        API 调用响应的历史记录
    """

    def __init__(self, api_key: str | None = None, base_url: str | None = None):
        """
        初始化 LLM 客户端

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
        self.call_history: list[str | dict[str, Any]] = []

    def call(
        self,
        messages: str | list[dict[str, str]],
        model: str = 'gpt-4o',
        response_format: str = 'text',
        temperature: float | None = None,
        top_p: float | None = None,
        frequency_penalty: float | None = None,
        presence_penalty: float | None = None,
        seed: int | None = None,
        max_tokens: int | None = None,
        stop: list[str] | None = None,
    ) -> str | dict[str, Any]:
        """
        调用 OpenAI Chat Completions API

        Parameters
        ----------
        model : str
            要使用的模型名称，例如 'gpt-4', 'gpt-3.5-turbo'
        messages : str or List[Dict[str, str]]
            消息列表或单个消息字符串。如果是字符串，将自动转换为用户消息
        response_format : {'text', 'json'}, default 'text'
            响应格式。'text' 返回纯文本，'json' 返回结构化JSON
        temperature : float, optional
            控制输出随机性的温度参数，范围 0-2。值越高输出越随机
        top_p : float, optional
            核采样参数，范围 0-1。与 temperature 一起控制输出多样性
        frequency_penalty : float, optional
            频率惩罚参数，范围 -2 到 2。正值减少重复内容
        presence_penalty : float, optional
            存在惩罚参数，范围 -2 到 2。正值鼓励谈论新主题
        seed : int, optional
            随机种子，用于获得可重现的输出
        max_tokens : int, optional
            生成的最大令牌数
        stop : List[str], optional
            停止序列列表，遇到这些序列时停止生成

        Returns
        -------
        str or Dict[str, Any]
            API 响应内容。如果 response_format='text' 返回字符串，
            如果 response_format='json' 返回解析后的字典

        Raises
        ------
        ValueError
            当 response_format 不是 'text' 或 'json' 时，
            或当请求 JSON 格式但消息中不包含 JSON 指令时
        json.JSONDecodeError
            当 JSON 响应无法解析时
        """
        # 验证响应格式
        if response_format not in ('text', 'json'):
            raise ValueError("response_format must be 'text' or 'json'")

        # 处理消息格式
        if isinstance(messages, str):
            messages = [{'role': 'user', 'content': messages}]
        if isinstance(messages, list) and not all(
            isinstance(msg, dict) and 'role' in msg and 'content' in msg
            for msg in messages
        ):
            raise ValueError("messages must be a list of dictionaries with 'role' and 'content'")
        if isinstance(messages, list):
            for msg in messages:
                if msg.get('role') not in ('user', 'assistant', 'system', 'developer'):
                    raise ValueError("Message role must be one of 'user', 'assistant', 'system', or 'developer'")
                if not isinstance(msg.get('content'), str):
                    raise ValueError('Message content must be a string')

        if response_format == 'json':
            self._validate_json_request(messages)

        params = self._build_request_params(
            model=model,
            messages=messages,
            response_format=response_format,
            temperature=temperature,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            seed=seed,
            max_tokens=max_tokens,
            stop=stop,
        )

        response = self.client.chat.completions.create(**params)
        content = response.choices[0].message.content.strip()


        if response_format == 'json':
            content = self._parse_json_response(content)

        # 记录调用历史
        if not self.call_history:
            self.call_history = messages.copy()
        else:
            self.call_history.append({'role': 'user', 'content': messages[-1]['content']})
        self.call_history.append({'role': 'assistant', 'content': content})
        return content

    def call_embed(
        self,
        input: str,
        model: str,
    ) -> list[float]:
        """
        获取文本的嵌入表示

        Parameters
        ----------
        input : str
            要嵌入的文本输入
        model : str
            使用的嵌入模型名称，例如 'text-embedding-3-large'

        Returns
        -------
        List[float]
            嵌入向量列表
        """
        response = self.client.embeddings.create(
            model=model,
            input=input,
        )
        if not response or not response.data:
            raise ValueError('No embedding data returned from OpenAI API.')
        return response.data[0].embedding


    def _validate_json_request(self, messages: list[dict[str, str]]) -> None:
        """
        验证 JSON 请求是否包含相关指令

        Parameters
        ----------
        messages : List[Dict[str, str]]
            消息列表

        Raises
        ------
        ValueError
            当消息内容中不包含 'json' 关键词时
        """
        has_json_instruction = any(
            'json' in str(message.get('content', '')).lower()
            for message in messages
            if isinstance(message, dict)
        )

        if not has_json_instruction:
            raise ValueError(
                "Message content does not contain 'json'. "
                'Please include JSON instructions in your prompt.',
            )

    def _build_request_params(self, **kwargs) -> dict[str, Any]:
        """
        构建 API 请求参数

        Parameters
        ----------
        **kwargs : dict
            包含所有请求参数的关键字参数

        Returns
        -------
        Dict[str, Any]
            构建好的请求参数字典
        """
        params = {
            'model': kwargs['model'],
            'messages': kwargs['messages'],
        }

        # 添加可选参数
        optional_params = [
            'temperature', 'top_p', 'frequency_penalty', 'presence_penalty',
            'seed', 'max_tokens', 'stop',
        ]

        for param in optional_params:
            value = kwargs.get(param)
            if value is not None:
                params[param] = value

        # 设置 JSON 响应格式
        if kwargs.get('response_format') == 'json':
            params['response_format'] = {'type': 'json_object'}

        return params

    def _parse_json_response(self, content: str) -> dict[str, Any]:
        """解析 JSON 响应内容"""
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return extract_json(content)

    def clear_history(self) -> None:
        """清空调用历史"""
        self.call_history.clear()

    def get_last_response(self) -> str | dict[str, Any] | None:
        """获取最后一次调用的响应"""
        return self.call_history[-1] if self.call_history else None

    def print_history(self) -> None:
        """打印调用历史记录"""
        print_conversation(self.call_history)

def extract_json(text: str) -> dict[str, Any]:
    """
    从字符串中提取第一个 JSON 对象并解析为 Python 字典

    支持以下格式：
    1. ```json ... ``` 代码块格式
    2. 直接的 { ... } JSON 对象格式

    Parameters
    ----------
    text : str
        包含 JSON 的文本字符串

    Returns
    -------
    Dict[str, Any]
        解析后的 JSON 字典

    Raises
    ------
    json.JSONDecodeError
        当无法找到或解析有效的 JSON 对象时

    Examples
    --------
    >>> text = '```json\\n{"name": "test", "value": 123}\\n```'
    >>> result = extract_json(text)
    >>> print(result)
    {'name': 'test', 'value': 123}

    >>> text = 'Some text {"key": "value"} more text'
    >>> result = extract_json(text)
    >>> print(result)
    {'key': 'value'}
    """
    # 首先尝试匹配代码块格式
    fence_pattern = r'```json\s*(\{.*?\})\s*```'
    match = re.search(fence_pattern, text, re.DOTALL)

    if match:
        candidate = match.group(1)
    else:
        # 尝试提取最外层的 JSON 对象
        candidate = _extract_json_braces(text)

    # 处理转义字符并解析
    candidate = candidate.replace(r'\n', '\n')
    return json.loads(candidate)


def _extract_json_braces(text: str) -> str:
    """
    从文本中提取第一个完整的 JSON 对象（基于大括号匹配）

    使用栈数据结构匹配大括号，提取第一个完整的 JSON 对象。

    Parameters
    ----------
    text : str
        输入文本字符串

    Returns
    -------
    str
        提取的 JSON 字符串

    Raises
    ------
    json.JSONDecodeError
        当未找到完整的 JSON 对象时

    Notes
    -----
    此函数仅基于大括号匹配进行提取，不验证 JSON 语法的正确性。
    实际的 JSON 语法验证由后续的 json.loads() 完成。
    """
    brace_stack = []
    start_idx = None

    for i, char in enumerate(text):
        if char == '{':
            if start_idx is None:
                start_idx = i
            brace_stack.append(char)
        elif char == '}' and brace_stack:
            brace_stack.pop()
            if not brace_stack and start_idx is not None:
                return text[start_idx:i + 1]

    raise json.JSONDecodeError('No complete JSON object found in text', text, 0)
