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

- **Simple API Interface**: Easy-to-use wrapper for OpenAI-compatible APIs
- **Message Support**: Accepts both string messages and structured conversation arrays
- **Conversation History**: Tracks and displays conversation history
- **Embedding Support**: Generate text embeddings with `call_embed` method
- **Template Integration**: Works with template-based prompts

## Usage Examples

### Single Question Answering

```python
from lmitf import BaseLLM

llm = BaseLLM()
response = llm.call(
    messages=[{'role': 'user', 'content': 'Who is the president of the United States?'}],
    response_format='text',
)
llm.print_history()
```

### Multi-turn Conversation

```python
# Continue conversation using call_history
q1 = "Where is the president from?"
res = llm.call(
    messages=llm.call_history + [{'role': 'user', 'content': q1}],
    response_format='text',
)
llm.print_history()
```

### Text Embeddings

```python
# Generate embeddings for text
text = "hello world"
embedding = llm.call_embed(
    input=text,
    model="text-embedding-3-large"
)
print(f"embedding shape: {embedding.shape}")
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
- `messages` (list): List of message dictionaries with 'role' and 'content'
- `response_format` (str): Response format (default: 'text')
- `model` (str): Model to use (default: "gpt-4o")
- `**kwargs`: Additional OpenAI API parameters like `temperature`

**Returns:**
- `str`: Generated response text

### call_embed()

Generate text embeddings.

**Parameters:**
- `input` (str): Text to embed
- `model` (str): Embedding model to use (e.g., "text-embedding-3-large")

**Returns:**
- `numpy.ndarray`: Text embedding vector

### print_history()

Display conversation history with formatted output.

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