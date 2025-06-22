# AI-Interface
[中文](https://github.com/colehank/AI-interface/README_zh.md)

---

## Overview

This project provides a flexible interface for interacting with OpenAI LLMs (Large Language Models), supporting both direct message calls and prompt template-based calls. It is designed for easy extension and integration with custom prompt templates.

## Installation

```bash
git clone https://github.com/colehank/AI-interface.git
cd AI-interface
pip install -r requirements.txt
```

## Environment Variables

Create a `.env` file in the project root (see `.env_example`):

```
OPENAI_API_KEY=your api key
OPENAI_BASE_URL=api endpoint
```

## Usage Example

### Basic LLM Call

```python
from src import BaseLLM

llm = BaseLLM()
response = llm.call(
    messages=[{"role": "user", "content": "Who is the president of the United States?"}],
    response_format='text',
)
print(response)
```

### Using Prompt Templates

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

### Print Conversation History

```python
llm.print_history()
template_llm.print_history()
```

## Class Overview

### BaseLLM
- Directly call OpenAI LLMs with message lists.
- Maintains call history.
- Supports text and JSON response formats.

### TemplateLLM
- Inherits from BaseLLM.
- Loads prompt templates from Python files.
- Fills variables in prompt templates for structured LLM calls.
- Example template variables: `passage`, `named_entities`.

## Prompt Template Mechanism
- Templates are Python files (see `src/datasets/llm_prompts/text2triples.py`).
- Each template must define `prompt_template` (list of messages) and `conditioned_frame` (string with variables).
- Variables in `conditioned_frame` (e.g., `$passage`, `$named_entities`) must be provided as arguments to `TemplateLLM.call()`.