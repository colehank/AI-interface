# LMITF Documentation

```{image} https://img.shields.io/pypi/v/lmitf.svg
:alt: PyPI Version
:target: https://pypi.org/project/lmitf/
```

```{image} https://img.shields.io/pypi/pyversions/lmitf.svg
:alt: Python Versions
:target: https://pypi.org/project/lmitf/
```

```{image} https://img.shields.io/github/license/colehank/AI-interface.svg
:alt: License
:target: https://github.com/colehank/AI-interface/blob/main/LICENSE
```

**LMITF (Large Model Interface)** is a flexible Python library that provides a unified interface for interacting with large language models (LLMs) and large vision models (LVMs). It simplifies the process of working with various AI models through aggregated API platforms.

## ✨ Key Features

:::{grid} 2
:gutter: 3

:::{grid-item-card} 🚀 Easy to Use
:class-card: text-center

Simple and intuitive API for both text and vision model interactions
:::

:::{grid-item-card} 🔧 Flexible Configuration
:class-card: text-center

Support for custom API endpoints and environment-based configuration
:::

:::{grid-item-card} 📊 Built-in Pricing
:class-card: text-center

Track API costs and usage with integrated pricing functionality
:::

:::{grid-item-card} 🎯 Template System
:class-card: text-center

Pre-built templates for common AI tasks and custom prompt management
:::

:::

## 🚀 Quick Start

### Installation

```bash
pip install lmitf
```

### Basic Usage

```python
from lmitf import BaseLLM

# Initialize the LLM client
llm = BaseLLM()

# Simple text generation
response = llm.call("Hello, how are you?")
print(response)

# JSON mode for structured output
data = llm.call_json("Generate a person's profile", model="gpt-4o")
print(data)
```

## 📖 Documentation Structure

```{toctree}
:maxdepth: 2
:caption: User Guide

installation
quickstart
examples
configuration
```

```{toctree}
:maxdepth: 2
:caption: API Reference

api/llm
api/lvm
api/templates
api/pricing
api/utils
```

```{toctree}
:maxdepth: 2
:caption: Advanced Topics

advanced/custom_templates
advanced/pricing_management
advanced/troubleshooting
```

```{toctree}
:maxdepth: 1
:caption: Development

contributing
changelog
license
```

## 🎯 Core Components

### BaseLLM
The main interface for text-based language models, supporting both streaming and non-streaming responses.

### BaseLVM  
Specialized interface for vision-language models that can process both text and images.

### TemplateLLM
Template-based system for managing and reusing common prompts and workflows.

### Pricing Module
Built-in cost tracking and API usage monitoring for better resource management.

## 🔗 External Links

- **GitHub Repository**: [https://github.com/colehank/AI-interface](https://github.com/colehank/AI-interface)
- **PyPI Package**: [https://pypi.org/project/lmitf/](https://pypi.org/project/lmitf/)
- **Issue Tracker**: [https://github.com/colehank/AI-interface/issues](https://github.com/colehank/AI-interface/issues)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/colehank/AI-interface/blob/main/LICENSE) file for details.

## 👨‍💻 Author

**Guohao Zhang** - [guohao2045@gmail.com](mailto:guohao2045@gmail.com)

---

```{admonition} Getting Help
:class: tip

If you need help or have questions:
- Check the [examples](examples.md) section
- Browse the [API reference](api/llm.md)
- Open an issue on [GitHub](https://github.com/colehank/AI-interface/issues)
```