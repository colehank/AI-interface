# Advanced Topics

## Custom Templates

### Creating Advanced Templates

Templates in LMITF are Python files that define prompt structures with variable substitution. Here's how to create sophisticated templates:

#### Template with Conditional Logic

```python
# advanced_template.py
import json

template = """
{%- if task_type == "analysis" %}
You are a data analyst. Analyze the following data:

Data: {data}

Focus on:
{%- if focus_areas %}
{%- for area in focus_areas %}
- {{ area }}
{%- endfor %}
{%- else %}
- Trends and patterns
- Key insights
- Recommendations
{%- endif %}

{%- elif task_type == "generation" %}
You are a content creator. Generate {content_type} about:

Topic: {topic}
Length: {length}
Style: {style}

{%- else %}
You are a helpful assistant. Please help with:
{request}
{%- endif %}
"""

defaults = {
    "length": "medium",
    "style": "professional",
    "focus_areas": None
}

def validate_inputs(**kwargs):
    """Custom validation function."""
    if kwargs.get("task_type") == "analysis" and not kwargs.get("data"):
        raise ValueError("Data is required for analysis tasks")
    
    if kwargs.get("task_type") == "generation" and not kwargs.get("topic"):
        raise ValueError("Topic is required for generation tasks")

def preprocess_inputs(**kwargs):
    """Preprocess inputs before template rendering."""
    if isinstance(kwargs.get("focus_areas"), str):
        kwargs["focus_areas"] = kwargs["focus_areas"].split(",")
    
    return kwargs
```

#### Template with Dynamic Prompts

```python
# dynamic_template.py
def generate_template(complexity="medium", domain="general"):
    """Generate template based on parameters."""
    
    if complexity == "simple":
        return "Please {action} the following: {input}"
    
    elif complexity == "medium":
        return """
        Task: {action}
        Context: {context}
        Input: {input}
        
        Please provide a {detail_level} response.
        """
    
    else:  # complex
        return """
        You are an expert in {domain}.
        
        Objective: {action}
        Background: {context}
        Constraints: {constraints}
        
        Input Data: {input}
        
        Please provide:
        1. Detailed analysis
        2. Step-by-step reasoning
        3. Confidence assessment
        4. Alternative approaches
        
        Format: {output_format}
        """

# Usage
template = generate_template("complex", "finance")
```

### Template Inheritance

```python
# base_template.py
base_system_prompt = """
You are a {role} with expertise in {domain}.
Your responses should be {tone} and {detail_level}.
"""

base_template = base_system_prompt + """
Task: {task}
Context: {context}
Input: {input}
"""

# specialized_template.py
from .base_template import base_template

template = base_template + """
Special Instructions:
{special_instructions}

Output Requirements:
- Format: {output_format}
- Length: {max_length}
- Include examples: {include_examples}
"""

defaults = {
    "role": "assistant",
    "tone": "professional",
    "detail_level": "comprehensive",
    "output_format": "structured",
    "include_examples": True
}
```

## Pricing Management

### Advanced Cost Tracking

```python
from lmitf import BaseLLM
from lmitf.pricing import PricingTracker
import datetime
import json

class AdvancedPricingTracker:
    def __init__(self):
        self.tracker = PricingTracker()
        self.session_costs = {}
        self.daily_limits = {}
    
    def set_daily_limit(self, limit_usd):
        """Set daily spending limit."""
        today = datetime.date.today().isoformat()
        self.daily_limits[today] = limit_usd
    
    def check_daily_limit(self):
        """Check if daily limit would be exceeded."""
        today = datetime.date.today().isoformat()
        if today not in self.daily_limits:
            return True
        
        today_cost = self.get_daily_cost(today)
        return today_cost < self.daily_limits[today]
    
    def track_call(self, model, input_tokens, output_tokens, cost):
        """Track individual API call."""
        call_data = {
            "timestamp": datetime.datetime.now().isoformat(),
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost": cost
        }
        
        self.tracker.add_call(call_data)
        return call_data
    
    def get_daily_cost(self, date=None):
        """Get total cost for a specific date."""
        if date is None:
            date = datetime.date.today().isoformat()
        
        return self.tracker.get_cost_by_date(date)
    
    def generate_cost_report(self, days=7):
        """Generate detailed cost report."""
        end_date = datetime.date.today()
        start_date = end_date - datetime.timedelta(days=days)
        
        report = {
            "period": f"{start_date} to {end_date}",
            "total_cost": 0,
            "daily_breakdown": {},
            "model_breakdown": {},
            "average_daily_cost": 0
        }
        
        # Implementation details...
        return report

# Usage
tracker = AdvancedPricingTracker()
tracker.set_daily_limit(10.00)  # $10 daily limit

llm = BaseLLM()

# Before making calls, check limit
if tracker.check_daily_limit():
    response = llm.call("Hello world", model="gpt-4")
    # Track the call cost
    tracker.track_call("gpt-4", 10, 5, 0.0003)
else:
    print("Daily limit reached!")
```

### Cost Optimization Strategies

```python
class CostOptimizedLLM:
    def __init__(self):
        self.models = {
            "cheap": "gpt-3.5-turbo",
            "balanced": "gpt-4o-mini", 
            "premium": "gpt-4o"
        }
        self.llm = BaseLLM()
    
    def smart_call(self, message, complexity="auto", max_cost=None):
        """Make LLM call with automatic model selection."""
        
        if complexity == "auto":
            complexity = self._assess_complexity(message)
        
        model = self._select_model(complexity, max_cost)
        
        return self.llm.call(message, model=model)
    
    def _assess_complexity(self, message):
        """Assess complexity of the request."""
        # Simple heuristics
        if len(message) < 100 and "?" in message:
            return "simple"
        elif any(word in message.lower() for word in ["analyze", "complex", "detailed"]):
            return "complex"
        else:
            return "medium"
    
    def _select_model(self, complexity, max_cost):
        """Select appropriate model based on complexity and cost."""
        if max_cost and max_cost < 0.001:
            return self.models["cheap"]
        
        if complexity == "simple":
            return self.models["cheap"]
        elif complexity == "medium":
            return self.models["balanced"]
        else:
            return self.models["premium"]

# Usage
optimized_llm = CostOptimizedLLM()

# Automatically selects appropriate model
response1 = optimized_llm.smart_call("What is 2+2?")  # Uses cheap model
response2 = optimized_llm.smart_call("Analyze the economic implications of AI", max_cost=0.01)  # Uses premium model if within budget
```

## Error Handling and Resilience

### Robust Error Handling

```python
import time
import random
from functools import wraps
from lmitf import BaseLLM

class ResilientLLM:
    def __init__(self, max_retries=3, backoff_factor=2):
        self.llm = BaseLLM()
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
    
    def retry_with_backoff(self, func):
        """Decorator for retry logic with exponential backoff."""
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(self.max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == self.max_retries - 1:
                        raise e
                    
                    # Exponential backoff with jitter
                    delay = (self.backoff_factor ** attempt) + random.uniform(0, 1)
                    print(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay:.2f}s...")
                    time.sleep(delay)
            
            return None
        return wrapper
    
    @retry_with_backoff
    def call_with_retry(self, message, **kwargs):
        """Make LLM call with automatic retry."""
        return self.llm.call(message, **kwargs)
    
    def call_with_fallback(self, message, fallback_models=None, **kwargs):
        """Try multiple models as fallbacks."""
        if fallback_models is None:
            fallback_models = ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"]
        
        for model in fallback_models:
            try:
                return self.llm.call(message, model=model, **kwargs)
            except Exception as e:
                print(f"Model {model} failed: {e}")
                continue
        
        raise Exception("All fallback models failed")

# Usage
resilient_llm = ResilientLLM()

# Automatic retry on failure
response = resilient_llm.call_with_retry("Hello world")

# Try multiple models
response = resilient_llm.call_with_fallback("Complex analysis task...")
```

### Circuit Breaker Pattern

```python
import time
from enum import Enum

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreakerLLM:
    def __init__(self, failure_threshold=5, timeout=60):
        self.llm = BaseLLM()
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
    
    def call(self, message, **kwargs):
        """Make LLM call with circuit breaker protection."""
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            response = self.llm.call(message, **kwargs)
            self._on_success()
            return response
        except Exception as e:
            self._on_failure()
            raise e
    
    def _should_attempt_reset(self):
        """Check if enough time has passed to attempt reset."""
        return (time.time() - self.last_failure_time) >= self.timeout
    
    def _on_success(self):
        """Handle successful call."""
        self.failure_count = 0
        self.state = CircuitState.CLOSED
    
    def _on_failure(self):
        """Handle failed call."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN

# Usage
circuit_llm = CircuitBreakerLLM()

try:
    response = circuit_llm.call("Hello world")
except Exception as e:
    print(f"Circuit breaker prevented call: {e}")
```

## Performance Optimization

### Connection Pooling

```python
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor
from lmitf import BaseLLM

class HighPerformanceLLM:
    def __init__(self, max_workers=10):
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.llm_pool = [BaseLLM() for _ in range(max_workers)]
    
    async def call_async(self, message, **kwargs):
        """Async LLM call using thread pool."""
        loop = asyncio.get_event_loop()
        
        # Get available LLM instance from pool
        llm = self.llm_pool.pop()
        
        try:
            # Run in thread pool
            response = await loop.run_in_executor(
                self.executor, 
                lambda: llm.call(message, **kwargs)
            )
            return response
        finally:
            # Return LLM to pool
            self.llm_pool.append(llm)
    
    async def batch_call_async(self, messages, **kwargs):
        """Process multiple messages concurrently."""
        tasks = [self.call_async(msg, **kwargs) for msg in messages]
        return await asyncio.gather(*tasks)

# Usage
async def main():
    perf_llm = HighPerformanceLLM()
    
    messages = ["Hello", "How are you?", "What's AI?", "Tell me a joke"]
    results = await perf_llm.batch_call_async(messages)
    
    for i, result in enumerate(results):
        print(f"Response {i+1}: {result}")

# Run async
asyncio.run(main())
```

### Streaming with Callbacks

```python
from lmitf import BaseLLM
from typing import Callable, Optional

class StreamingLLM:
    def __init__(self):
        self.llm = BaseLLM()
    
    def stream_call(
        self, 
        message: str, 
        on_token: Optional[Callable[[str], None]] = None,
        on_complete: Optional[Callable[[str], None]] = None,
        **kwargs
    ):
        """Stream LLM response with callbacks."""
        full_response = ""
        
        try:
            stream = self.llm.call(message, stream=True, **kwargs)
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    token = chunk.choices[0].delta.content
                    full_response += token
                    
                    if on_token:
                        on_token(token)
            
            if on_complete:
                on_complete(full_response)
                
            return full_response
            
        except Exception as e:
            print(f"Streaming error: {e}")
            return full_response

# Usage
streaming_llm = StreamingLLM()

def print_token(token):
    print(token, end="", flush=True)

def on_complete(response):
    print(f"\n\nComplete response: {len(response)} characters")

response = streaming_llm.stream_call(
    "Write a short story about AI",
    on_token=print_token,
    on_complete=on_complete
)
```

## Advanced Integration Patterns

### Plugin System

```python
from abc import ABC, abstractmethod
from typing import Dict, Any

class LMITFPlugin(ABC):
    """Base class for LMITF plugins."""
    
    @abstractmethod
    def before_call(self, message: str, **kwargs) -> Dict[str, Any]:
        """Called before LLM call."""
        pass
    
    @abstractmethod
    def after_call(self, response: str, metadata: Dict[str, Any]) -> str:
        """Called after LLM call."""
        pass

class LoggingPlugin(LMITFPlugin):
    def before_call(self, message, **kwargs):
        print(f"[LOG] Calling LLM with message: {message[:50]}...")
        return {"timestamp": time.time()}
    
    def after_call(self, response, metadata):
        duration = time.time() - metadata["timestamp"]
        print(f"[LOG] Response received in {duration:.2f}s")
        return response

class CachePlugin(LMITFPlugin):
    def __init__(self):
        self.cache = {}
    
    def before_call(self, message, **kwargs):
        cache_key = hash(message)
        if cache_key in self.cache:
            return {"cached": True, "response": self.cache[cache_key]}
        return {"cached": False, "cache_key": cache_key}
    
    def after_call(self, response, metadata):
        if not metadata["cached"]:
            self.cache[metadata["cache_key"]] = response
        return response

class PluginManager:
    def __init__(self):
        self.plugins = []
        self.llm = BaseLLM()
    
    def add_plugin(self, plugin: LMITFPlugin):
        self.plugins.append(plugin)
    
    def call(self, message, **kwargs):
        # Before call hooks
        metadata = {}
        for plugin in self.plugins:
            plugin_data = plugin.before_call(message, **kwargs)
            if plugin_data.get("cached"):
                return plugin_data["response"]
            metadata.update(plugin_data)
        
        # Make the actual call
        response = self.llm.call(message, **kwargs)
        
        # After call hooks
        for plugin in self.plugins:
            response = plugin.after_call(response, metadata)
        
        return response

# Usage
manager = PluginManager()
manager.add_plugin(LoggingPlugin())
manager.add_plugin(CachePlugin())

response = manager.call("What is AI?")  # Logged and cached
response = manager.call("What is AI?")  # Retrieved from cache
```

These advanced topics showcase the flexibility and extensibility of LMITF for complex, production-ready applications.