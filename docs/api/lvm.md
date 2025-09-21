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

- **Image Generation**: Create images from text prompts with `create` method
- **Image Editing**: Edit existing images with `edit` method
- **Template Integration**: Works with template-based image generation prompts

## Usage Examples

### Image Generation

```python
from lmitf import BaseLVM

vlm = BaseLVM()
result = vlm.create(
    prompt="A beautiful landscape with mountains and a river",
    model='gpt-image-1',
)
```

### Image Editing

```python
# Edit existing image
edited_result = vlm.edit(result, "Add flying cats in the sky")
```

### Template-based Image Generation

```python
# Use predefined templates
template = lmitf.prompts.lvm_prompts['character_ref']
template_lvm = TemplateLLM(template)

# Generate image with template parameters
result = template_lvm.call(
    CharacterName="Hero",
    RefCharacter="base64_image_data",
    Size="1024x1024",
    Character="warrior",
    Style="fantasy",
    GenPrompt="Create a fantasy warrior scene"
)
```


## Method Reference

### create()

Generate images from text prompts.

**Parameters:**
- `prompt` (str): Text description of desired image
- `model` (str): Image generation model to use (e.g., 'gpt-image-1')

**Returns:**
- Generated image object/data

### edit()

Edit existing images with text prompts.

**Parameters:**
- `image`: Previously generated image object
- `prompt` (str): Description of desired changes

**Returns:**
- Edited image object/data

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

## Best Practices

1. **Clear Prompts**: Be specific about what you want to generate
2. **Template Usage**: Use predefined templates for consistent results
3. **Model Selection**: Choose appropriate models based on your needs

## Related Classes

- [BaseLLM](llm.md) - For text-only language tasks
- [TemplateLLM](templates.md) - For template-based workflows