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

- **Cost Tracking**: Monitor API usage costs in real-time
- **Pricing Data**: Fetch current pricing from model providers
- **Usage Analytics**: Analyze spending patterns and usage trends
- **Multiple Providers**: Support for various AI model providers

## Usage Examples

### Basic Pricing Information

```python
from lmitf.pricing import get_pricing_info, calculate_cost

# Get current pricing data
pricing = get_pricing_info()
print(pricing)

# Calculate cost for a specific usage
cost = calculate_cost(
    model="gpt-4",
    input_tokens=1000,
    output_tokens=500
)
print(f"Estimated cost: ${cost:.4f}")
```

### Integration with BaseLLM

```python
from lmitf import BaseLLM
from lmitf.pricing import track_usage

llm = BaseLLM()

# Make a call and track usage
response = llm.call("Hello world", model="gpt-4")

# Track the usage for cost calculation
usage_data = track_usage(
    model="gpt-4",
    prompt_tokens=10,
    completion_tokens=5
)
print(f"Call cost: ${usage_data['cost']:.4f}")
```

### Batch Cost Analysis

```python
# Analyze costs for multiple calls
calls_data = [
    {"model": "gpt-4", "input_tokens": 1000, "output_tokens": 200},
    {"model": "gpt-3.5-turbo", "input_tokens": 800, "output_tokens": 150},
    {"model": "gpt-4", "input_tokens": 1200, "output_tokens": 300},
]

total_cost = 0
for call in calls_data:
    cost = calculate_cost(**call)
    total_cost += cost
    print(f"{call['model']}: ${cost:.4f}")

print(f"Total cost: ${total_cost:.4f}")
```

## Function Reference

### get_pricing_info()

Fetch current pricing information from API providers.

**Parameters:**
- `provider` (str, optional): Specific provider to query
- `cache_timeout` (int, optional): Cache timeout in seconds

**Returns:**
- `dict`: Pricing information for various models

### calculate_cost()

Calculate the cost for a specific API call.

**Parameters:**
- `model` (str): Model name
- `input_tokens` (int): Number of input tokens
- `output_tokens` (int): Number of output tokens  
- `provider` (str, optional): Provider name

**Returns:**
- `float`: Estimated cost in USD

### track_usage()

Track usage for cost monitoring.

**Parameters:**
- `model` (str): Model used
- `prompt_tokens` (int): Input token count
- `completion_tokens` (int): Output token count
- `timestamp` (datetime, optional): Call timestamp

**Returns:**
- `dict`: Usage data with cost information

## Cost Tracking Example

```python
from lmitf import BaseLLM
from lmitf.pricing import UsageTracker

# Initialize tracker
tracker = UsageTracker()

# Initialize LLM
llm = BaseLLM()

# Make calls and track usage
for prompt in ["Hello", "How are you?", "Tell me a joke"]:
    response = llm.call(prompt, model="gpt-4")
    
    # Track the usage (you'd get token counts from the actual response)
    tracker.add_usage(
        model="gpt-4",
        input_tokens=len(prompt.split()),  # Simplified
        output_tokens=len(response.split()),  # Simplified
        cost=calculate_cost("gpt-4", len(prompt.split()), len(response.split()))
    )

# Get usage summary
summary = tracker.get_summary()
print(f"Total calls: {summary['total_calls']}")
print(f"Total cost: ${summary['total_cost']:.4f}")
print(f"Average cost per call: ${summary['avg_cost_per_call']:.4f}")
```

## Usage Analytics

### Daily Usage Report

```python
from lmitf.pricing import generate_usage_report
from datetime import date, timedelta

# Generate report for the last 7 days
report = generate_usage_report(
    start_date=date.today() - timedelta(days=7),
    end_date=date.today()
)

print("Daily Usage Report:")
for day, data in report.items():
    print(f"{day}: {data['calls']} calls, ${data['cost']:.4f}")
```

### Model Comparison

```python
# Compare costs across different models
models = ["gpt-4", "gpt-3.5-turbo", "claude-3-opus"]
sample_input = 1000  # tokens
sample_output = 500  # tokens

print("Cost Comparison:")
for model in models:
    cost = calculate_cost(model, sample_input, sample_output)
    print(f"{model}: ${cost:.4f}")
```

## Configuration

### API Keys for Pricing Data

Some pricing functions may require API keys to fetch real-time data:

```python
import os

# Set environment variables for pricing APIs
os.environ["OPENAI_API_KEY"] = "your-openai-key"
os.environ["ANTHROPIC_API_KEY"] = "your-anthropic-key"
```

### Custom Pricing Data

You can provide custom pricing data:

```python
custom_pricing = {
    "gpt-4": {
        "input_cost_per_1k": 0.03,
        "output_cost_per_1k": 0.06
    },
    "gpt-3.5-turbo": {
        "input_cost_per_1k": 0.001,
        "output_cost_per_1k": 0.002
    }
}

cost = calculate_cost(
    model="gpt-4",
    input_tokens=1000,
    output_tokens=500,
    pricing_data=custom_pricing
)
```

## Integration with Jupyter Notebooks

```python
# For Jupyter notebook usage tracking
from lmitf.pricing import notebook_usage_tracker

# Start tracking in a notebook
tracker = notebook_usage_tracker()

# Your LLM calls here...
# The tracker will automatically capture usage

# Display results
tracker.display_summary()
```

## Best Practices

1. **Regular Monitoring**: Check usage and costs regularly
2. **Budget Alerts**: Set up alerts for spending thresholds
3. **Model Selection**: Choose appropriate models based on cost/performance
4. **Batch Processing**: Group similar requests to optimize costs
5. **Cache Results**: Cache responses to avoid redundant API calls

## Related Modules

- [BaseLLM](llm.md) - Base language model interface
- [BaseLVM](lvm.md) - Vision model interface
- [Utils](utils.md) - Utility functions