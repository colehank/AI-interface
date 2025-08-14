# Installation

## Requirements

LMITF requires Python 3.10 or higher.

## Install from PyPI

The easiest way to install LMITF is from PyPI:

```bash
pip install lmitf
```

## Install from Source

For the latest development version, you can install directly from the GitHub repository:

```bash
git clone https://github.com/colehank/AI-interface.git
cd AI-interface
pip install -r requirements.txt
pip install -e .
```

## Dependencies

LMITF depends on the following packages:

- `openai>=1.0` - OpenAI Python client
- `pandas>=2.3` - Data manipulation and analysis
- `python-dotenv>=1.0` - Environment variable management
- `wasabi>=1.1` - Pretty printing and formatting
- `pillow>=9.0` - Image processing for vision models

These dependencies will be automatically installed when you install LMITF.

## Development Installation

If you plan to contribute to the project, install the development dependencies:

```bash
git clone https://github.com/colehank/AI-interface.git
cd AI-interface
pip install -r requirements.txt
pip install -e ".[dev]"
```

## Verification

To verify your installation, run:

```python
import lmitf
print(lmitf.__version__)
```

You should see the version number printed without any errors.

## Configuration

After installation, you'll need to set up your API credentials. See the [Configuration](configuration.md) section for details.