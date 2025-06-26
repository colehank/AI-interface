# 中文说明

## 项目简介

该项目为与聚合API平台交互提供了一个灵活的接口，支持直接消息调用和基于模板的提示调用。
## 安装方法

```bash
git clone https://github.com/colehank/AI-interface.git
cd AI-interface
pip install -r requirements.txt
```

## 环境变量

在项目根目录下创建`.env`文件（参考`.env_example`）：

```
OPENAI_API_KEY=你的API密钥
OPENAI_BASE_URL=API地址
```

## 使用示例
LLM见[example_llm.py](https://github.com/colehank/AI-interface/blob/main/example_llm.ipynb),
LVM见[example_lvm.py](https://github.com/colehank/AI-interface/blob/main/example_lvm.ipynb)
