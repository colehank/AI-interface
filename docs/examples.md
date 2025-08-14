# Examples and Use Cases

This section provides comprehensive examples of using LMITF for various AI tasks.

## Basic Examples

### Simple Text Generation

```python
from lmitf import BaseLLM

llm = BaseLLM()

# Basic text generation
response = llm.call("Write a haiku about programming")
print(response)
```

### Structured Data Extraction

```python
# Extract structured information
prompt = """
Extract the following information from this text and return as JSON:
- Person's name
- Company
- Position
- Location

Text: "Sarah Johnson works as a Senior Data Scientist at TechCorp in San Francisco."
"""

data = llm.call_json(prompt)
print(data)
# Output: {"name": "Sarah Johnson", "company": "TechCorp", "position": "Senior Data Scientist", "location": "San Francisco"}
```

## Vision Model Examples

### Image Analysis

```python
from lmitf import BaseLVM

lvm = BaseLVM()

# Analyze a single image
response = lvm.call(
    messages="Describe this image in detail and identify any text",
    image_path="screenshot.png"
)
print(response)
```

### Document Processing

```python
# OCR and document understanding
response = lvm.call(
    messages="""
    Extract all text from this document and:
    1. Summarize the key points
    2. Identify any dates, numbers, or names
    3. Note the document type
    """,
    image_path="invoice.pdf"
)
print(response)
```

### Multi-Image Comparison

```python
# Compare multiple images
images = ["before.jpg", "after.jpg"] 
response = lvm.call(
    messages="Compare these before and after images. What changed?",
    image_path=images
)
print(response)
```

## Template Examples

### Custom Analysis Template

```python
# analysis_template.py
template = """
You are an expert {domain} analyst.

Task: Analyze the following {data_type} and provide insights.

Data: {input_data}

Please provide:
1. Summary of key findings
2. Notable patterns or trends  
3. Recommendations for {target_audience}
4. Confidence level in your analysis

Format your response as {output_format}.
"""

defaults = {
    "domain": "business",
    "data_type": "dataset", 
    "output_format": "structured report",
    "target_audience": "stakeholders"
}

required_vars = ["input_data"]
```

Usage:

```python
from lmitf import TemplateLLM

template_llm = TemplateLLM("analysis_template.py")

result = template_llm.call_template(
    domain="financial",
    data_type="quarterly earnings report",
    input_data="Q3 revenue increased 15% YoY to $2.3M...",
    target_audience="investors",
    output_format="executive summary"
)
print(result)
```

## Advanced Use Cases

### Conversational AI

```python
from lmitf import BaseLLM
from lmitf.utils import print_conversation

class ConversationManager:
    def __init__(self):
        self.llm = BaseLLM()
        self.conversation = [
            {"role": "system", "content": "You are a helpful AI assistant."}
        ]
    
    def add_user_message(self, message):
        self.conversation.append({"role": "user", "content": message})
    
    def get_response(self):
        response = self.llm.call(self.conversation)
        self.conversation.append({"role": "assistant", "content": response})
        return response
    
    def show_conversation(self):
        print_conversation(self.conversation)

# Usage
chat = ConversationManager()
chat.add_user_message("What's the weather like today?")
response = chat.get_response()
print(response)

chat.add_user_message("What should I wear?")
response = chat.get_response()
chat.show_conversation()
```

### Batch Processing

```python
import pandas as pd
from lmitf import BaseLLM

def process_reviews_batch(reviews_df):
    """Process customer reviews for sentiment and themes."""
    llm = BaseLLM()
    results = []
    
    for _, row in reviews_df.iterrows():
        prompt = f"""
        Analyze this customer review:
        
        Review: "{row['review_text']}"
        Product: {row['product_name']}
        
        Provide:
        1. Sentiment (positive/negative/neutral)
        2. Key themes (max 3)
        3. Action items (if any)
        
        Format as JSON.
        """
        
        try:
            analysis = llm.call_json(prompt)
            analysis['review_id'] = row['id']
            results.append(analysis)
        except Exception as e:
            print(f"Error processing review {row['id']}: {e}")
    
    return pd.DataFrame(results)

# Usage
reviews = pd.DataFrame({
    'id': [1, 2, 3],
    'review_text': [
        "Great product, fast delivery!",
        "Poor quality, disappointed with purchase",
        "Average product, nothing special"
    ],
    'product_name': ['Widget A', 'Widget B', 'Widget A']
})

results = process_reviews_batch(reviews)
print(results)
```

### Code Analysis

```python
def analyze_code(code_snippet, language="python"):
    """Analyze code for quality, bugs, and improvements."""
    llm = BaseLLM()
    
    prompt = f"""
    Analyze this {language} code:
    
    ```{language}
    {code_snippet}
    ```
    
    Provide:
    1. Code quality assessment (1-10 scale)
    2. Potential bugs or issues
    3. Performance improvements
    4. Best practices recommendations
    5. Refactored version (if improvements needed)
    
    Format as JSON with clear sections.
    """
    
    return llm.call_json(prompt)

# Usage
code = '''
def calculate_average(numbers):
    total = 0
    for num in numbers:
        total += num
    return total / len(numbers)
'''

analysis = analyze_code(code)
print(analysis)
```

## Real-World Applications

### Content Moderation

```python
class ContentModerator:
    def __init__(self):
        self.llm = BaseLLM()
        
    def moderate_content(self, content, content_type="text"):
        prompt = f"""
        Moderate this {content_type} content for:
        1. Inappropriate language
        2. Hate speech
        3. Spam/promotional content
        4. Misinformation
        5. Privacy violations
        
        Content: "{content}"
        
        Return JSON with:
        - is_appropriate: boolean
        - violations: list of issues found
        - confidence: 0-100
        - suggested_action: "approve", "review", or "reject"
        """
        
        return self.llm.call_json(prompt)

# Usage
moderator = ContentModerator()
result = moderator.moderate_content("Check out this amazing product!")
print(result)
```

### Data Visualization Helper

```python
def generate_chart_code(data_description, chart_type="bar"):
    """Generate Python plotting code from data description."""
    llm = BaseLLM()
    
    prompt = f"""
    Generate Python code using matplotlib/seaborn to create a {chart_type} chart.
    
    Data description: {data_description}
    
    Requirements:
    1. Include sample data generation if needed
    2. Proper labels and titles
    3. Clean, professional styling
    4. Comments explaining key steps
    
    Return only the Python code, no explanations.
    """
    
    return llm.call(prompt)

# Usage
code = generate_chart_code(
    "Monthly sales data for 2023, showing revenue trends", 
    "line"
)
print(code)
```

### Email Assistant

```python
class EmailAssistant:
    def __init__(self):
        self.llm = BaseLLM()
    
    def compose_email(self, purpose, recipient_type, key_points, tone="professional"):
        prompt = f"""
        Compose an email with these details:
        
        Purpose: {purpose}
        Recipient: {recipient_type}
        Key points to include: {key_points}
        Tone: {tone}
        
        Include:
        - Appropriate subject line
        - Professional greeting
        - Clear body with key points
        - Proper closing
        
        Format as JSON with 'subject' and 'body' fields.
        """
        
        return self.llm.call_json(prompt)
    
    def summarize_email(self, email_content):
        prompt = f"""
        Summarize this email:
        
        {email_content}
        
        Provide:
        1. Main purpose/request
        2. Key action items
        3. Deadline (if any)
        4. Priority level
        
        Format as JSON.
        """
        
        return self.llm.call_json(prompt)

# Usage
assistant = EmailAssistant()

email = assistant.compose_email(
    purpose="Request meeting to discuss project timeline",
    recipient_type="project manager",
    key_points="Timeline concerns, resource allocation, next milestones",
    tone="polite but urgent"
)
print(email)
```

## Performance Optimization

### Caching Responses

```python
import hashlib
import json
from functools import lru_cache

class CachedLLM:
    def __init__(self):
        self.llm = BaseLLM()
        self.cache = {}
    
    def _hash_input(self, messages, model):
        """Create hash for caching."""
        input_str = json.dumps({"messages": messages, "model": model}, sort_keys=True)
        return hashlib.md5(input_str.encode()).hexdigest()
    
    def call_cached(self, messages, model="gpt-4o", cache_ttl=3600):
        """Call with caching support."""
        cache_key = self._hash_input(messages, model)
        
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        response = self.llm.call(messages, model=model)
        self.cache[cache_key] = response
        return response

# Usage
cached_llm = CachedLLM()
response1 = cached_llm.call_cached("What is AI?")  # API call
response2 = cached_llm.call_cached("What is AI?")  # Cached result
```

### Parallel Processing

```python
import concurrent.futures
from lmitf import BaseLLM

def process_item(item):
    """Process a single item."""
    llm = BaseLLM()
    return llm.call(f"Analyze this item: {item}")

def process_items_parallel(items, max_workers=5):
    """Process multiple items in parallel."""
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(process_item, item) for item in items]
        results = []
        
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                print(f"Error processing item: {e}")
                results.append(None)
    
    return results

# Usage
items = ["Product A", "Product B", "Product C", "Product D"]
results = process_items_parallel(items)
print(results)
```

## Integration Examples

### Flask Web Application

```python
from flask import Flask, request, jsonify
from lmitf import BaseLLM

app = Flask(__name__)
llm = BaseLLM()

@app.route('/analyze', methods=['POST'])
def analyze_text():
    data = request.json
    text = data.get('text', '')
    
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    
    try:
        analysis = llm.call_json(f"Analyze this text for sentiment and key themes: {text}")
        return jsonify(analysis)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message', '')
    
    response = llm.call(message)
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(debug=True)
```

### Jupyter Notebook Integration

```python
# Cell 1: Setup
from lmitf import BaseLLM, BaseLVM
from lmitf.utils import print_conversation
import pandas as pd
import matplotlib.pyplot as plt

llm = BaseLLM()
lvm = BaseLVM()

# Cell 2: Data Analysis
data = pd.read_csv('sales_data.csv')
analysis_prompt = f"""
Analyze this sales data summary:
{data.describe().to_string()}

Provide insights about:
1. Trends and patterns
2. Anomalies or outliers  
3. Business recommendations
"""

insights = llm.call(analysis_prompt)
print(insights)

# Cell 3: Visualization
chart_prompt = f"""
Generate matplotlib code to visualize this data:
{data.head().to_string()}

Create a meaningful chart that shows the key trends.
"""

chart_code = llm.call(chart_prompt)
print("Generated code:")
print(chart_code)

# Execute the generated code
exec(chart_code)
```

## Testing and Validation

### Unit Testing with LMITF

```python
import unittest
from unittest.mock import patch, MagicMock
from lmitf import BaseLLM

class TestLLMIntegration(unittest.TestCase):
    def setUp(self):
        self.llm = BaseLLM()
    
    @patch('lmitf.base_llm.OpenAI')
    def test_call_basic(self, mock_openai):
        # Mock the OpenAI response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Test response"
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        # Test the call
        result = self.llm.call("Test message")
        self.assertEqual(result, "Test response")
    
    def test_json_parsing(self):
        # Test JSON response parsing
        with patch.object(self.llm, 'call', return_value='{"key": "value"}'):
            result = self.llm.call_json("Test")
            self.assertEqual(result, {"key": "value"})

if __name__ == '__main__':
    unittest.main()
```

These examples demonstrate the flexibility and power of LMITF across various domains and use cases. The library's simple interface makes it easy to integrate AI capabilities into any Python application.