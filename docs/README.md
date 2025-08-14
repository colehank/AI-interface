# LMITF Documentation

This directory contains the comprehensive documentation for LMITF (Large Model Interface), built with Sphinx and featuring a beautiful modern theme.

## 📚 Documentation Structure

The documentation is organized into several main sections:

### User Guide
- **[Installation](installation.md)** - Installation instructions and requirements
- **[Quick Start](quickstart.md)** - Get up and running quickly
- **[Configuration](configuration.md)** - Environment setup and configuration options
- **[Examples](examples.md)** - Comprehensive examples and use cases

### API Reference
- **[BaseLLM](api/llm.md)** - Core language model interface
- **[BaseLVM](api/lvm.md)** - Vision-language model interface  
- **[TemplateLLM](api/templates.md)** - Template-based prompt system
- **[Pricing](api/pricing.md)** - Cost tracking and pricing utilities
- **[Utils](api/utils.md)** - Utility functions

### Advanced Topics
- **[Custom Templates](advanced/custom_templates.md)** - Creating advanced templates
- **[Pricing Management](advanced/pricing_management.md)** - Cost optimization strategies
- **[Troubleshooting](advanced/troubleshooting.md)** - Common issues and solutions

### Development
- **[Contributing](contributing.md)** - Guidelines for contributors
- **[Changelog](changelog.md)** - Version history and changes
- **[License](license.md)** - MIT License information

## 🏗️ Building the Documentation

### Prerequisites

1. **Install Python Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Documentation Dependencies**
   ```bash
   pip install -r docs/requirements.txt
   ```

### Build Commands

**Build HTML Documentation:**
```bash
cd docs
sphinx-build -b html . _build/html
```

**Or use Make:**
```bash
cd docs
make html
```

**Live Reload (for development):**
```bash
cd docs
make livehtml
# or
sphinx-autobuild -b html . _build/html
```

### Viewing the Documentation

After building, open `_build/html/index.html` in your browser:

```bash
# macOS
open _build/html/index.html

# Linux
xdg-open _build/html/index.html

# Windows
start _build/html/index.html
```

## 🎨 Theme and Features

The documentation uses the modern **Furo** theme with:

- ✨ Beautiful, responsive design
- 🌙 Dark/light mode support
- 📱 Mobile-friendly layout
- 🔍 Full-text search
- 📋 Copy-to-clipboard code blocks
- 🎯 Syntax highlighting
- 📚 Cross-references and navigation
- 🏷️ MyST Markdown support

## 📝 Writing Documentation

### Markdown Format

Documentation is written in **MyST Markdown**, which supports:

- Standard Markdown syntax
- Sphinx directives and roles
- Code fencing with syntax highlighting
- Admonitions (notes, warnings, tips)
- Cross-references
- Grid layouts and design elements

### Example Structure

```markdown
# Page Title

Brief introduction to the topic.

## Section Header

Content with examples:

```python
from lmitf import BaseLLM

llm = BaseLLM()
response = llm.call("Hello world")
print(response)
```

## Related Topics

- [Link to other page](other-page.md)
- [API Reference](api/llm.md)
```

### Adding New Pages

1. Create a new `.md` file in the appropriate directory
2. Add it to the `toctree` in `index.md` or the relevant section
3. Rebuild the documentation

## 🔧 Configuration

The documentation configuration is in `conf.py`:

- **Project Info**: Name, author, version
- **Extensions**: Enabled Sphinx extensions
- **Theme**: Furo theme with custom styling
- **MyST**: Markdown parser configuration
- **Autodoc**: Automatic API documentation generation

## 🚀 Deployment

The documentation can be deployed to various platforms:

### GitHub Pages
```bash
# Build and deploy to gh-pages branch
sphinx-build -b html . ../docs-build
# Push to gh-pages branch
```

### Read the Docs
- Connect your GitHub repository
- Documentation builds automatically on push

### Static Hosting
- Upload the `_build/html` directory to any web server

## 🤝 Contributing to Documentation

1. **Fork the repository**
2. **Make your changes** to the `.md` files
3. **Test locally** by building the docs
4. **Submit a pull request**

### Documentation Guidelines

- Write clear, concise explanations
- Include code examples for all features
- Use proper MyST Markdown syntax
- Add cross-references where helpful
- Test all code examples
- Follow the existing structure and style

## 📊 Documentation Metrics

The built documentation includes:

- **16 pages** of comprehensive content
- **API documentation** auto-generated from docstrings  
- **100+ code examples** across all topics
- **Full search functionality**
- **Mobile responsive design**

## 🆘 Help and Support

- **Issues**: Report documentation issues on GitHub
- **Discussions**: Join community discussions
- **Contributing**: See the contributing guide for help

---

**Built with ❤️ using Sphinx and Furo**