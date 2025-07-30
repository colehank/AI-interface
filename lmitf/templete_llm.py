from __future__ import annotations

import importlib.util
import os
import os.path as op
import re
from string import Template

import pandas as pd
from dotenv import load_dotenv
from wasabi import msg

from .base_llm import BaseLLM
load_dotenv()

class TemplateLLM(BaseLLM):

    def __init__(self, template_path: str, api_key: str = None, base_url: str = None):
        super().__init__(
            api_key=api_key or os.getenv('OPENAI_API_KEY'),
            base_url=base_url or os.getenv('OPENAI_BASE_URL'),
        )
        """初始化模板LLM客户端
        """
        assert op.exists(template_path), f'Template file does not exist: {template_path}'
        assert template_path.endswith('.py'), 'Template file must be a Python file (.py)'
        self._load_template(template_path)
        self.template_path = template_path
        msg.text(f'Template loaded from \n{template_path}')

    def _load_template(self, template_path: str):
        """
        加载prompt模板文件并解析其中的模板变量

        Parameters
        ----------
        template_path : str
            模板文件的路径(.py文件)
        """
        if not op.exists(template_path):
            raise FileNotFoundError(
                f'Template file not found: {template_path}',
            )


        spec = importlib.util.spec_from_file_location(
            'template_module', template_path,
        )
        template_module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(template_module)
        except Exception as e:
            raise ImportError(f'Failed to load template module: {e}')

        if not hasattr(template_module, 'prompt_template'):
            raise AttributeError(
                f"Template module must define 'prompt_template' attribute: \n{template_path}",
            )
        if not hasattr(template_module, 'conditioned_frame'):
            raise AttributeError(
                f"Template module must define 'conditioned_frame' attribute: \n{template_path}",
            )

        self.prompt_template = getattr(template_module, 'prompt_template')
        self.conditioned_frame = getattr(template_module, 'conditioned_frame')
        self.template_obj = Template(template_module.conditioned_frame)

        variables = re.findall(r'\$(\w+)', self.conditioned_frame)
        variables = list(set(variables))  # 去重
        if not variables:
            raise ValueError(
                f'No variables found in conditioned_frame: \n{self.conditioned_frame}',
            )
        self.variables = variables

    def _fill(self, **kwargs):
        """
        使用提供的参数替换模板中的变量

        Parameters
        ----------
        **kwargs
            要替换的模板变量

        Returns
        -------
        str
            替换后的文本
        """
        # 检查输入的kwargs是否和variables匹配
        missing_vars = set(self.variables) - set(kwargs.keys())
        if missing_vars:
            raise ValueError(f'Missing required variables: {missing_vars}')

        extra_vars = set(kwargs.keys()) - set(self.variables)
        if extra_vars:
            raise ValueError(f'Unexpected variables provided: {extra_vars}')

        prompt = self.prompt_template.copy()
        prompt[-1]['content'] = self.template_obj.substitute(**kwargs)
        return prompt

    def call(self, **kwargs):
        """
        调用LLM，生成响应

        Returns
        -------
        str
            LLM的响应内容
        """
        if not self.prompt_template:
            raise ValueError('Prompt template is not defined.')
        template_vars = {
            k: v for k, v in kwargs.items() if k in self.variables
        }
        messages = self._fill(**template_vars)
        non_template_kwargs = {
            k: v for k, v in kwargs.items() if k not in self.variables
        }
        response = super().call(messages=messages, **non_template_kwargs)

        return response

    def _repr_html_(self):
        """
        返回HTML格式的表示，以DataFrame形式显示模板信息
        """

        data = {
            'Name': [op.basename(self.template_path)],
            'Variables to fill': [', '.join(self.variables)],
        }

        df = pd.DataFrame(data)
        df.index = ['Template Info']
        return df.T._repr_html_()
