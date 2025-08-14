# Configuration Guide

LMITF provides flexible configuration options to adapt to different environments and use cases.

## Environment Variables

The primary way to configure LMITF is through environment variables.

### Basic Configuration

Create a `.env` file in your project root:

```env
# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_BASE_URL=https://api.openai.com/v1

# Optional: Organization ID
OPENAI_ORG_ID=your-org-id

# Optional: Project ID  
OPENAI_PROJECT_ID=your-project-id
```

### Alternative API Providers

LMITF works with any OpenAI-compatible API:

```env
# Azure OpenAI
OPENAI_API_KEY=your-azure-key
OPENAI_BASE_URL=https://your-resource.openai.azure.com/

# Local/Self-hosted
OPENAI_API_KEY=local-key
OPENAI_BASE_URL=http://localhost:8080/v1

# Other providers (Anthropic, etc.)
OPENAI_API_KEY=your-provider-key
OPENAI_BASE_URL=https://api.provider.com/v1
```

## Manual Configuration

You can also configure clients directly in code:

### BaseLLM Configuration

```python
from lmitf import BaseLLM

# Direct configuration
llm = BaseLLM(
    api_key="your-api-key",
    base_url="https://your-endpoint.com/v1"
)

# Environment-based (recommended)
llm = BaseLLM()  # Uses env vars automatically
```

### BaseLVM Configuration

```python
from lmitf import BaseLVM

# Direct configuration
lvm = BaseLVM(
    api_key="your-api-key", 
    base_url="https://your-endpoint.com/v1"
)
```

### TemplateLLM Configuration

```python
from lmitf import TemplateLLM

# Template with custom API settings
template_llm = TemplateLLM(
    template_path="path/to/template.py",
    api_key="your-key",
    base_url="https://your-endpoint.com/v1"
)
```

## Configuration Files

### .env File Structure

```env
# =====================================
# LMITF Configuration
# =====================================

# Primary API Configuration
OPENAI_API_KEY=sk-your-key-here
OPENAI_BASE_URL=https://api.openai.com/v1

# Optional Settings
OPENAI_ORG_ID=org-your-org-id
OPENAI_PROJECT_ID=proj-your-project-id

# Rate Limiting
REQUESTS_PER_MINUTE=60
MAX_RETRIES=3

# Logging
LOG_LEVEL=INFO
LOG_FILE=lmitf.log

# Pricing Configuration
PRICING_CACHE_TTL=3600
COST_TRACKING_ENABLED=true
```

### Python Configuration

```python
# config.py
import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
API_CONFIG = {
    "api_key": os.getenv("OPENAI_API_KEY"),
    "base_url": os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
    "organization": os.getenv("OPENAI_ORG_ID"),
    "project": os.getenv("OPENAI_PROJECT_ID"),
}

# Model Defaults
DEFAULT_MODELS = {
    "llm": "gpt-4o",
    "lvm": "gpt-4-vision-preview",
    "cheap": "gpt-3.5-turbo"
}

# Usage in your code
from lmitf import BaseLLM
from config import API_CONFIG, DEFAULT_MODELS

llm = BaseLLM(**API_CONFIG)
response = llm.call("Hello", model=DEFAULT_MODELS["llm"])
```

## Advanced Configuration

### Custom Client Settings

```python
from openai import OpenAI
from lmitf import BaseLLM

# Custom OpenAI client
custom_client = OpenAI(
    api_key="your-key",
    base_url="https://your-endpoint.com/v1",
    timeout=30.0,
    max_retries=5,
    default_headers={"Custom-Header": "value"}
)

# Use with LMITF (advanced usage)
llm = BaseLLM()
llm.client = custom_client
```

### Proxy Configuration

For corporate environments with proxies:

```python
import os

# Set proxy environment variables
os.environ["HTTP_PROXY"] = "http://proxy.company.com:8080"
os.environ["HTTPS_PROXY"] = "https://proxy.company.com:8080"

# Or configure in Python
import httpx

proxy_client = httpx.Client(proxies={
    "http://": "http://proxy.company.com:8080",
    "https://": "https://proxy.company.com:8080"
})
```

## Environment-Specific Configuration

### Development

```env
# .env.development
OPENAI_API_KEY=sk-dev-key-here
OPENAI_BASE_URL=https://api.openai.com/v1
LOG_LEVEL=DEBUG
COST_TRACKING_ENABLED=true
```

```python
# Load development config
from dotenv import load_dotenv

load_dotenv('.env.development')
```

### Production

```env
# .env.production  
OPENAI_API_KEY=sk-prod-key-here
OPENAI_BASE_URL=https://api.openai.com/v1
LOG_LEVEL=WARNING
COST_TRACKING_ENABLED=true
REQUESTS_PER_MINUTE=100
```

### Testing

```env
# .env.test
OPENAI_API_KEY=sk-test-key-here
OPENAI_BASE_URL=http://localhost:8080/v1
LOG_LEVEL=ERROR
COST_TRACKING_ENABLED=false
```

## Docker Configuration

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'
services:
  app:
    build: .
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - OPENAI_BASE_URL=${OPENAI_BASE_URL}
    env_file:
      - .env
```

### Dockerfile

```dockerfile
FROM python:3.11-slim

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application
COPY . /app
WORKDIR /app

# Environment variables can be set at runtime
ENV OPENAI_API_KEY=""
ENV OPENAI_BASE_URL="https://api.openai.com/v1"

CMD ["python", "app.py"]
```

## Configuration Validation

```python
import os
from lmitf import BaseLLM

def validate_config():
    """Validate LMITF configuration."""
    required_vars = ["OPENAI_API_KEY"]
    
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        raise ValueError(f"Missing required environment variables: {missing}")
    
    # Test API connection
    try:
        llm = BaseLLM()
        response = llm.call("test", max_tokens=1)
        print("✅ Configuration valid")
    except Exception as e:
        print(f"❌ Configuration error: {e}")

# Run validation
validate_config()
```

## Best Practices

1. **Use Environment Variables**: Store sensitive data in environment variables
2. **Separate Environments**: Use different configs for dev/staging/prod
3. **Version Control**: Never commit API keys to version control
4. **Key Rotation**: Regularly rotate API keys
5. **Monitoring**: Monitor API usage and costs
6. **Validation**: Validate configuration on startup

## Troubleshooting

### Common Issues

1. **API Key Not Found**
   ```python
   # Check if key is loaded
   import os
   print(os.getenv("OPENAI_API_KEY"))
   ```

2. **Wrong Base URL**
   ```python
   # Verify endpoint
   llm = BaseLLM(base_url="https://correct-endpoint.com/v1")
   ```

3. **Proxy Issues**
   ```python
   # Check proxy settings
   import os
   print(os.getenv("HTTP_PROXY"))
   print(os.getenv("HTTPS_PROXY"))
   ```

## Related Topics

- [Installation](installation.md) - Installing LMITF
- [Quick Start](quickstart.md) - Getting started guide
- [API Reference](api/llm.md) - Detailed API documentation