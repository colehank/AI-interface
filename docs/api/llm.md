# BaseLLM API Reference

```{eval-rst}
.. automodule:: lmitf.base_llm
   :members:
   :undoc-members:
   :show-inheritance:
```

## Overview

The `BaseLLM` class provides a simplified interface for interacting with OpenAI's Chat Completions API. It handles authentication, request formatting, and response processing automatically.

## Class Reference

### BaseLLM

```{eval-rst}
.. autoclass:: lmitf.base_llm.BaseLLM
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__
```

## Key Features

- **Automatic Configuration**: Uses environment variables for API key and base URL
- **Flexible Input**: Accepts both string messages and structured conversation arrays
- **JSON Mode**: Built-in support for structured JSON responses
- **History Tracking**: Maintains a history of all API calls
- **Streaming Support**: Real-time response streaming
- **Error Handling**: Comprehensive error handling and logging

## Usage Examples

### Basic Text Generation

```python
from lmitf import BaseLLM

llm = BaseLLM()
response = llm.call("What is machine learning?")
print(response)
```

### JSON Mode

```python
# Get structured output
profile = llm.call_json(
    "Generate a user profile with name, age, and occupation",
    model="gpt-4"
)
print(profile)  # Returns a dictionary
```

### Conversation with Context

```python
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What's the capital of France?"},
    {"role": "assistant", "content": "The capital of France is Paris."},
    {"role": "user", "content": "What's its population?"}
]

response = llm.call(messages, model="gpt-4")
print(response)
```

### Streaming Responses

```python
# Stream responses for real-time output
response_stream = llm.call(
    "Write a short story about AI",
    model="gpt-4",
    stream=True
)

for chunk in response_stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
```

## Configuration

### Environment Variables

The `BaseLLM` class automatically reads configuration from environment variables:

```bash
export OPENAI_API_KEY="your-api-key"
export OPENAI_BASE_URL="https://api.openai.com/v1"
```

### Manual Configuration

You can also provide credentials directly:

```python
llm = BaseLLM(
    api_key="your-api-key",
    base_url="https://your-custom-endpoint.com/v1"
)
```

## Method Reference

### call()

Main method for generating text responses.

**Parameters:**
- `messages` (str | list): Input message(s)
- `model` (str): Model to use (default: "gpt-4o")
- `stream` (bool): Enable streaming responses
- `**kwargs`: Additional OpenAI API parameters

**Returns:**
- `str`: Generated response text (non-streaming)
- `Iterator`: Streaming response chunks (streaming)

### call_json()

Generate structured JSON responses.

**Parameters:**
- `messages` (str | list): Input message(s)  
- `model` (str): Model to use (default: "gpt-4o")
- `**kwargs`: Additional OpenAI API parameters

**Returns:**
- `dict`: Parsed JSON response

## Error Handling

The class includes comprehensive error handling:

```python
try:
    response = llm.call("Hello", model="invalid-model")
except Exception as e:
    print(f"API Error: {e}")
```

## Best Practices

1. **Use Environment Variables**: Store API credentials in `.env` files
2. **Handle Errors**: Always wrap API calls in try-catch blocks
3. **Monitor Usage**: Check `call_history` to track API usage
4. **Choose Appropriate Models**: Use different models based on task complexity
5. **Use JSON Mode**: For structured data extraction tasks

## Related Classes

- [BaseLVM](lvm.md) - For vision-language tasks
- [TemplateLLM](templates.md) - For template-based workflows