# Quick Start Guide

This guide will help you get started with LMITF quickly.

## Basic Setup

### 1. Install LMITF

```bash
pip install lmitf
```

### 2. Set up Environment Variables

Create a `.env` file in your project root:

```env
OPENAI_API_KEY=your-api-key-here
OPENAI_BASE_URL=https://api.openai.com/v1
```

### 3. Your First LLM Call

```python
from lmitf import BaseLLM

# Initialize the client
llm = BaseLLM()

# Make a simple call
response = llm.call("What is artificial intelligence?")
print(response)
```

## Working with Different Models

### Text Generation

```python
from lmitf import BaseLLM

llm = BaseLLM()

# Use different models
gpt4_response = llm.call("Explain quantum computing", model="gpt-4")
gpt35_response = llm.call("Explain quantum computing", model="gpt-3.5-turbo")

print("GPT-4:", gpt4_response)
print("GPT-3.5:", gpt35_response)
```

### JSON Mode

For structured outputs:

```python
# Get JSON response
profile = llm.call_json(
    "Generate a user profile with name, age, and occupation",
    model="gpt-4"
)
print(profile)
# Output: {"name": "John Doe", "age": 30, "occupation": "Software Engineer"}
```

### Conversation History

```python
# Multi-turn conversation
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What's the weather like?"},
    {"role": "assistant", "content": "I don't have access to real-time weather data."},
    {"role": "user", "content": "What should I wear for a rainy day?"}
]

response = llm.call(messages)
print(response)
```

## Vision Models

### Working with Images

```python
from lmitf import BaseLVM

lvm = BaseLVM()

# Analyze an image
response = lvm.call(
    messages="What do you see in this image?",
    image_path="path/to/your/image.jpg"
)
print(response)
```

### Multiple Images

```python
# Analyze multiple images
images = ["image1.jpg", "image2.jpg", "image3.jpg"]
response = lvm.call(
    messages="Compare these images and describe the differences",
    image_path=images
)
print(response)
```

## Template System

### Using Pre-built Templates

```python
from lmitf import TemplateLLM

template_llm = TemplateLLM()

# Use a pre-built template
result = template_llm.call_template(
    template_name="text2triples",
    text="John works at Google as a software engineer."
)
print(result)
```

### Custom Templates

```python
# Define a custom template
custom_template = """
Task: Summarize the following text in {word_count} words.

Text: {text}

Summary:
"""

# Use the custom template
response = llm.call(
    custom_template.format(
        word_count=50,
        text="Your long text here..."
    )
)
print(response)
```

## Pricing and Usage Tracking

### Check API Costs

```python
from lmitf.pricing import get_pricing_info

# Get current pricing information
pricing = get_pricing_info()
print(pricing)

# Track usage in your calls
llm = BaseLLM()
response = llm.call("Hello world")

# Check call history for usage tracking
print(f"Total calls made: {len(llm.call_history)}")
```

## Streaming Responses

### Real-time Text Generation

```python
# Stream responses for long generations
response_stream = llm.call(
    "Write a detailed explanation of machine learning",
    model="gpt-4",
    stream=True
)

for chunk in response_stream:
    print(chunk.choices[0].delta.content, end="", flush=True)
```

## Error Handling

```python
try:
    response = llm.call("Hello world", model="invalid-model")
except Exception as e:
    print(f"Error: {e}")
    # Handle the error appropriately
```

## Next Steps

Now that you've got the basics down, explore:

- [Detailed Examples](examples.md) - More comprehensive use cases
- [Configuration](configuration.md) - Advanced configuration options
- [API Reference](api/llm.md) - Complete API documentation

```{admonition} Pro Tip
:class: tip

Set up your `.env` file once and LMITF will automatically use your credentials across all projects in that environment.
```