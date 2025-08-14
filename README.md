# LMITF - Large Model Interface

[![PyPI Version](https://img.shields.io/pypi/v/lmitf.svg)](https://pypi.org/project/lmitf/)
[![Python Versions](https://img.shields.io/pypi/pyversions/lmitf.svg)](https://pypi.org/project/lmitf/)
[![License](https://img.shields.io/github/license/colehank/AI-interface.svg)](https://github.com/colehank/AI-interface/blob/main/LICENSE)
[![Documentation](https://img.shields.io/badge/docs-online-brightgreen.svg)](https://colehank.github.io/AI-interface/)

LMITF (Large Model Interface) 为与大型语言模型和视觉模型交互提供了一个灵活、简洁的Python接口。

## ✨ 特性

- 🚀 **简单易用** - 直观的API设计，快速上手
- 🔧 **灵活配置** - 支持多种API端点和环境配置
- 📊 **内置定价** - 集成成本追踪和使用分析
- 🎯 **模板系统** - 预构建模板和自定义提示管理
- 🖼️ **视觉模型** - 支持图像分析和多模态AI任务
- 📖 **完整文档** - 详尽的使用指南和API参考

## 📚 文档

**完整文档**: [https://colehank.github.io/AI-interface/](https://colehank.github.io/AI-interface/)

- [快速入门](https://colehank.github.io/AI-interface/quickstart.html)
- [API参考](https://colehank.github.io/AI-interface/api/llm.html)
- [使用示例](https://colehank.github.io/AI-interface/examples.html)
- [配置指南](https://colehank.github.io/AI-interface/configuration.html)

## 🚀 快速开始

### 安装

```bash
pip install lmitf
```

### 基本使用

```python
from lmitf import BaseLLM

# 初始化客户端
llm = BaseLLM()

# 简单文本生成
response = llm.call("你好，请介绍一下人工智能")
print(response)

# JSON模式获取结构化输出
data = llm.call_json("生成一个用户档案，包含姓名、年龄和职业")
print(data)
```

### 视觉模型

```python  
from lmitf import BaseLVM

lvm = BaseLVM()

# 图像分析
response = lvm.call(
    messages="描述这张图片的内容",
    image_path="image.jpg"
)
print(response)
```

## 📋 项目简介

LMITF (Large Model Interface) 为与聚合API平台交互提供了一个灵活的接口，支持：

- **文本生成** - 基于BaseLLM的语言模型交互
- **图像理解** - 基于BaseLVM的视觉语言模型
- **模板系统** - TemplateLLM支持复用提示模板
- **成本管理** - 内置定价追踪和使用分析

## 🔧 环境配置

创建`.env`文件：

```env
OPENAI_API_KEY=你的API密钥
OPENAI_BASE_URL=https://api.openai.com/v1
```

## 📖 更多示例

- **LLM使用**: [example_llm.ipynb](https://github.com/colehank/AI-interface/blob/main/example_llm.ipynb)
- **视觉模型**: [example_lvm.ipynb](https://github.com/colehank/AI-interface/blob/main/example_lvm.ipynb)  
- **定价查询**: [example_price.ipynb](https://github.com/colehank/AI-interface/blob/main/example_price.ipynb)

## 🤝 贡献

欢迎贡献代码！请查看[贡献指南](https://colehank.github.io/AI-interface/contributing.html)了解详情。

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 👨‍💻 作者

**Guohao Zhang** - [guohao2045@gmail.com](mailto:guohao2045@gmail.com)

---

🌟 **如果这个项目对您有帮助，请给个星标支持！**