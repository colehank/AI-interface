# BaseLVM API Reference

```{eval-rst}
.. automodule:: lmitf.base_lvm
   :members:
   :undoc-members:
   :show-inheritance:
```

## Overview

The `BaseLVM` class provides an interface for working with Large Vision Models (LVMs) that can process both text and images. It's designed for multimodal AI tasks that require understanding visual content.

## Class Reference

### BaseLVM

```{eval-rst}
.. autoclass:: lmitf.base_lvm.BaseLVM
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__
```

## Key Features

- **Multimodal Processing**: Handle both text and image inputs
- **Multiple Image Support**: Process multiple images in a single request
- **Flexible Image Input**: Support for file paths, URLs, and PIL Image objects
- **Automatic Encoding**: Handle base64 encoding transparently
- **OpenAI Integration**: Built on OpenAI's vision models

## Usage Examples

### Basic Image Analysis

```python
from lmitf import BaseLVM

lvm = BaseLVM()

# Analyze a single image
response = lvm.call(
    messages="What do you see in this image?",
    image_path="path/to/image.jpg"
)
print(response)
```

### Multiple Image Analysis

```python
# Compare multiple images
images = ["image1.jpg", "image2.jpg", "image3.jpg"]
response = lvm.call(
    messages="Compare these images and describe the differences",
    image_path=images
)
print(response)
```

### Image with Complex Prompt

```python
# Detailed analysis with specific instructions
prompt = """
Analyze this image and provide:
1. A description of the main objects
2. The color palette used
3. Any text visible in the image
4. The overall mood or atmosphere
"""

response = lvm.call(
    messages=prompt,
    image_path="screenshot.png",
    model="gpt-4-vision-preview"
)
print(response)
```

### Image Generation (if supported)

```python
# Generate images using create method
image_response = lvm.create(
    prompt="A futuristic city skyline at sunset",
    size="1024x1024",
    quality="standard",
    n=1
)
print(image_response)
```

## Supported Image Formats

- **JPEG** (.jpg, .jpeg)
- **PNG** (.png) 
- **GIF** (.gif)
- **WebP** (.webp)
- **BMP** (.bmp)

## Input Methods

### File Paths

```python
# Single image file
response = lvm.call("Describe this image", image_path="photo.jpg")

# Multiple image files  
response = lvm.call("Compare these", image_path=["img1.jpg", "img2.png"])
```

### PIL Image Objects

```python
from PIL import Image

# Load image with PIL
img = Image.open("photo.jpg")
response = lvm.call("What's in this image?", image_path=img)
```

### URLs (if supported by model)

```python
# Remote image URL
response = lvm.call(
    "Analyze this image",
    image_path="https://example.com/image.jpg"
)
```

## Method Reference

### call()

Main method for vision-language tasks.

**Parameters:**
- `messages` (str | list): Text prompt or conversation
- `image_path` (str | list | PIL.Image): Image(s) to analyze
- `model` (str): Vision model to use
- `max_tokens` (int): Maximum response length
- `**kwargs`: Additional API parameters

**Returns:**
- `str`: Generated response describing the image(s)

### create()

Generate images from text prompts (if supported).

**Parameters:**
- `prompt` (str): Text description of desired image
- `size` (str): Image dimensions (e.g., "1024x1024")  
- `quality` (str): Image quality ("standard" or "hd")
- `n` (int): Number of images to generate

**Returns:**
- `dict`: Response with generated image URLs/data

## Configuration

### Environment Setup

```bash
export OPENAI_API_KEY="your-api-key"
export OPENAI_BASE_URL="https://api.openai.com/v1"
```

### Manual Configuration

```python
lvm = BaseLVM(
    api_key="your-api-key",
    base_url="https://your-endpoint.com/v1"
)
```

## Error Handling

```python
try:
    response = lvm.call("Describe this", image_path="missing.jpg")
except FileNotFoundError:
    print("Image file not found")
except Exception as e:
    print(f"API Error: {e}")
```

## Best Practices

1. **Image Quality**: Use high-quality images for better analysis
2. **File Size**: Keep images under 20MB for optimal performance
3. **Batch Processing**: Process multiple related images together
4. **Clear Prompts**: Be specific about what you want to analyze
5. **Error Handling**: Always handle file and network errors

## Common Use Cases

### Document Analysis

```python
# OCR and document understanding
response = lvm.call(
    "Extract all text from this document and summarize the key points",
    image_path="document.pdf"
)
```

### Visual QA

```python
# Answer questions about images
response = lvm.call(
    "How many people are in this photo and what are they doing?",
    image_path="group_photo.jpg"
)
```

### Chart/Graph Analysis

```python
# Analyze data visualizations
response = lvm.call(
    "What trends do you see in this chart? Provide key insights.",
    image_path="sales_chart.png"
)
```

## Related Classes

- [BaseLLM](llm.md) - For text-only language tasks
- [TemplateLLM](templates.md) - For template-based workflows