# 中文说明

## 项目简介

本项目为OpenAI大语言模型（LLM）提供了灵活的接口，支持直接消息调用和基于模板的调用，便于扩展和集成自定义Prompt模板。

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

### 基础LLM调用

```python
from src import BaseLLM

llm = BaseLLM()
response = llm.call(
    messages=[{"role": "user", "content": "Who is the president of the United States?"}],
    response_format='text',
)
print(response)
```

### 使用Prompt模板

```python
from src import TemplateLLM, prompts

prompt_file = prompts.llm_prompts['text2triples']
template_llm = TemplateLLM(prompt_file)

response = template_llm.call(
    passage="XiaoMing is a Chinese student from Beijing Normal University",
    named_entities='["Chinese", "Beijing Normal University", "XiaoMing"]',
    model='gpt-4o',
    response_format='json',
)
print(response)
```

### 打印对话历史

```python
llm.print_history()
template_llm.print_history()
```

## 类说明

### BaseLLM
- 直接调用OpenAI LLM，传入消息列表。
- 自动维护调用历史。
- 支持文本和JSON两种响应格式。

### TemplateLLM
- 继承自BaseLLM。
- 从Python文件加载Prompt模板。
- 自动填充模板变量，结构化调用LLM。
- 示例模板变量：`passage`、`named_entities`。

## Prompt模板机制
- 模板为Python文件（见`src/datasets/llm_prompts/text2triples.py`）。
- 每个模板需定义`prompt_template`（消息列表）和`conditioned_frame`（含变量的字符串）。
- `conditioned_frame`中的变量（如`$passage`、`$named_entities`）需作为参数传递给`TemplateLLM.call()`。 