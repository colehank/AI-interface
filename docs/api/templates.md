# TemplateLLM API Reference

```{eval-rst}
.. automodule:: lmitf.templete_llm
   :members:
   :undoc-members:
   :show-inheritance:
```

## Overview

The `TemplateLLM` class extends `BaseLLM` to provide template-based prompt management. It allows you to define reusable prompt templates with variables, making it easier to maintain consistent AI interactions across your application.

## Class Reference

### TemplateLLM

```{eval-rst}
.. autoclass:: lmitf.templete_llm.TemplateLLM
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__
```

## Key Features

- **Template System**: Define reusable prompt templates with variables
- **Python-based Templates**: Templates are Python files for maximum flexibility
- **Variable Substitution**: Support for complex variable substitution patterns
- **Inheritance**: Extends all `BaseLLM` functionality
- **Batch Processing**: Process multiple inputs with the same template

## Template File Format

Templates are Python files that define prompt structures:

```python
# example_template.py
template = """
Task: {task_description}

Input: {input_text}

Please provide a detailed analysis following these guidelines:
1. {guideline_1}
2. {guideline_2}
3. {guideline_3}

Output format: {output_format}
"""

# Optional: Define default values
defaults = {
    "output_format": "JSON",
    "task_description": "Analysis Task"
}

# Optional: Define validation rules
required_vars = ["input_text", "guideline_1", "guideline_2", "guideline_3"]
```

## Usage Examples

### Basic Template Usage

```python
from lmitf import TemplateLLM

# Load a template
template_llm = TemplateLLM("path/to/template.py")

# Use the template
response = template_llm.call_template(
    input_text="Your text here",
    guideline_1="Be comprehensive",
    guideline_2="Use specific examples", 
    guideline_3="Provide actionable insights"
)
print(response)
```

### Pre-built Templates

LMITF includes several pre-built templates:

```python
# Text to triples extraction
from lmitf.datasets.llm_prompts.text2triples import template

template_llm = TemplateLLM("lmitf/datasets/llm_prompts/text2triples.py")
result = template_llm.call_template(
    text="John works at Google as a software engineer."
)
print(result)  # Extracts relationship triples
```

### Custom Template Creation

Create your own template file:

```python
# my_template.py
template = """
You are a {role} expert. 

Task: {task}

Context: {context}

Requirements:
{requirements}

Please provide your {output_type}.
"""

defaults = {
    "role": "AI assistant",
    "output_type": "response"
}

required_vars = ["task", "context", "requirements"]
```

Use the custom template:

```python
template_llm = TemplateLLM("my_template.py")

response = template_llm.call_template(
    role="data science",
    task="Analyze this dataset",
    context="E-commerce sales data from 2023",
    requirements="Focus on trends and anomalies",
    output_type="detailed report"
)
```

### Batch Processing

Process multiple inputs with the same template:

```python
inputs = [
    {"text": "First document content"},
    {"text": "Second document content"},
    {"text": "Third document content"}
]

results = []
for input_data in inputs:
    result = template_llm.call_template(**input_data)
    results.append(result)
```

## Method Reference

### call_template()

Execute a template with provided variables.

**Parameters:**
- `**kwargs`: Template variables as keyword arguments

**Returns:**
- `str`: Generated response using the template

### reload_template()

Reload the template file (useful during development).

```python
# After modifying the template file
template_llm.reload_template()
```

## Template Best Practices

### 1. Clear Variable Names

```python
# Good
template = "Analyze {dataset_name} for {analysis_type} patterns"

# Avoid
template = "Analyze {x} for {y} patterns"
```

### 2. Provide Defaults

```python
defaults = {
    "tone": "professional",
    "format": "markdown",
    "max_length": "500 words"
}
```

### 3. Use Required Variables

```python
required_vars = ["input_text", "task_type"]
# Will raise error if these aren't provided
```

### 4. Template Documentation

```python
"""
Template: Content Analysis
Description: Analyzes content for sentiment, topics, and key insights
Variables:
  - content (required): Text content to analyze
  - focus_areas (optional): Specific areas to focus on
  - output_format (optional): JSON, markdown, or plain text
"""
```

## Advanced Features

### Conditional Logic in Templates

```python
template = """
{%- if analysis_type == "detailed" %}
Please provide a comprehensive analysis including:
1. Summary
2. Key themes
3. Recommendations
{%- else %}
Please provide a brief summary.
{%- endif %}

Content: {content}
"""
```

### Template Inheritance

```python
# base_template.py
base_template = """
System: You are a {role}.
Task: {task}
"""

# specific_template.py
from .base_template import base_template

template = base_template + """
Additional instructions: {instructions}
Input: {input_data}
"""
```

## Built-in Templates

### text2triples

Extracts relationship triples from text:

```python
template_llm = TemplateLLM("lmitf/datasets/llm_prompts/text2triples.py")
result = template_llm.call_template(
    text="Apple was founded by Steve Jobs in Cupertino."
)
# Output: [("Apple", "founded_by", "Steve Jobs"), ("Apple", "located_in", "Cupertino")]
```

## Error Handling

```python
try:
    template_llm = TemplateLLM("nonexistent_template.py")
except FileNotFoundError:
    print("Template file not found")

try:
    result = template_llm.call_template(missing_required_var="value")
except KeyError as e:
    print(f"Missing required variable: {e}")
```

## Related Classes

- [BaseLLM](llm.md) - Base functionality for language models
- [BaseLVM](lvm.md) - For vision-language tasks