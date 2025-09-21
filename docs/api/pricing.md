# Pricing API Reference

```{eval-rst}
.. automodule:: lmitf.pricing
   :members:
   :undoc-members:
   :show-inheritance:
```

## Overview

The pricing module provides functionality to track API costs, monitor usage, and fetch current pricing information from various AI model providers.

## Key Features

- **Model Price Lookup**: Get pricing information for specific models
- **Balance Checking**: Check account balance for API providers
- **Simple Integration**: Easy integration with pricing APIs

## Usage Examples

### Get Model Pricing

```python
from lmitf.pricing import DMX

# Initialize pricing API client
dmxapi = DMX('https://www.dmxapi.cn/pricing')

# Get pricing for specific model
price = dmxapi.get_model_price('gpt-4o')
print(f'gpt-4o计费方式：按{price.billing_type}')
print(f'输入价格：{price.input_per_m}元/百万tokens')
print(f'输出价格：{price.output_per_m}元/百万tokens')
```

### Check Account Balance

```python
# Check remaining balance
balance = dmxapi.fetch_balance()
print(f'用户余额信息：{balance}')
```

## Class Reference

### DMX

A client for interacting with pricing APIs.

**Parameters:**
- `url` (str): Base URL for the pricing API

### Methods

#### get_model_price(model)

Get pricing information for a specific model.

**Parameters:**
- `model` (str): Model name (e.g., 'gpt-4o')

**Returns:**
- Price object with `billing_type`, `input_per_m`, `output_per_m` attributes

#### fetch_balance()

Get account balance information.

**Returns:**
- `float`: Remaining account balance

## Best Practices

1. **Regular Monitoring**: Check pricing information before making API calls
2. **Model Selection**: Choose appropriate models based on cost/performance

## Related Modules

- [BaseLLM](llm.md) - Base language model interface
- [BaseLVM](lvm.md) - Vision model interface
- [Utils](utils.md) - Utility functions