# Pricing Management

## Cost Tracking and Optimization

Effective pricing management is crucial for production applications using AI models. This guide covers advanced pricing strategies, cost tracking, and optimization techniques.

## Advanced Cost Tracking

### Real-time Cost Monitoring

```python
from lmitf import BaseLLM
from lmitf.pricing import PricingTracker
import datetime
import threading
import time

class RealTimeCostTracker:
    def __init__(self, alert_threshold=5.0):
        self.tracker = PricingTracker()
        self.alert_threshold = alert_threshold
        self.daily_spend = 0.0
        self.running = False
        self.lock = threading.Lock()
    
    def start_monitoring(self):
        """Start background monitoring."""
        self.running = True
        monitor_thread = threading.Thread(target=self._monitor_loop)
        monitor_thread.daemon = True
        monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop background monitoring."""
        self.running = False
    
    def _monitor_loop(self):
        """Background monitoring loop."""
        while self.running:
            with self.lock:
                if self.daily_spend > self.alert_threshold:
                    self._send_alert(f"Daily spend exceeded ${self.alert_threshold}")
            time.sleep(60)  # Check every minute
    
    def track_call(self, cost):
        """Track individual API call cost."""
        with self.lock:
            self.daily_spend += cost
        self.tracker.add_cost(cost)
    
    def _send_alert(self, message):
        """Send cost alert."""
        print(f"🚨 COST ALERT: {message}")
        # Could integrate with email, Slack, etc.

# Usage
cost_tracker = RealTimeCostTracker(alert_threshold=10.0)
cost_tracker.start_monitoring()

llm = BaseLLM()
response = llm.call("Hello world")
cost_tracker.track_call(0.0001)  # Track the cost
```

### Budget Management

```python
class BudgetManager:
    def __init__(self):
        self.budgets = {}
        self.spending = {}
    
    def set_budget(self, category, amount, period="daily"):
        """Set budget for a category."""
        self.budgets[category] = {
            "amount": amount,
            "period": period,
            "start_date": datetime.date.today()
        }
        self.spending[category] = 0.0
    
    def check_budget(self, category, cost):
        """Check if spending would exceed budget."""
        if category not in self.budgets:
            return True
        
        current_spend = self.spending.get(category, 0)
        return (current_spend + cost) <= self.budgets[category]["amount"]
    
    def record_spending(self, category, cost):
        """Record spending against budget."""
        if category not in self.spending:
            self.spending[category] = 0.0
        
        self.spending[category] += cost
        
        # Check if budget exceeded
        budget = self.budgets.get(category, {})
        if self.spending[category] > budget.get("amount", float('inf')):
            self._budget_alert(category)
    
    def _budget_alert(self, category):
        """Send budget alert."""
        budget = self.budgets[category]
        spent = self.spending[category]
        print(f"⚠️  Budget exceeded for {category}: ${spent:.4f} / ${budget['amount']:.4f}")
    
    def get_budget_status(self):
        """Get status of all budgets."""
        status = {}
        for category, budget in self.budgets.items():
            spent = self.spending.get(category, 0)
            remaining = budget["amount"] - spent
            status[category] = {
                "budget": budget["amount"],
                "spent": spent,
                "remaining": remaining,
                "percentage_used": (spent / budget["amount"]) * 100
            }
        return status

# Usage
budget_mgr = BudgetManager()
budget_mgr.set_budget("development", 50.0, "daily")
budget_mgr.set_budget("production", 200.0, "daily")

# Before making expensive calls
if budget_mgr.check_budget("development", 0.50):
    # Make API call
    response = llm.call("Complex analysis task")
    budget_mgr.record_spending("development", 0.50)
else:
    print("Budget exceeded, skipping call")
```

## Cost Optimization Strategies

### Intelligent Model Selection

```python
class SmartModelSelector:
    def __init__(self):
        self.model_costs = {
            "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002},
            "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
            "gpt-4o": {"input": 0.03, "output": 0.06},
            "gpt-4": {"input": 0.03, "output": 0.06}
        }
        
        self.model_capabilities = {
            "gpt-3.5-turbo": {"complexity": 3, "accuracy": 7},
            "gpt-4o-mini": {"complexity": 4, "accuracy": 8},
            "gpt-4o": {"complexity": 9, "accuracy": 9},
            "gpt-4": {"complexity": 10, "accuracy": 10}
        }
    
    def select_model(self, task_complexity, accuracy_requirement, budget_limit=None):
        """Select optimal model based on requirements."""
        suitable_models = []
        
        for model, caps in self.model_capabilities.items():
            if (caps["complexity"] >= task_complexity and 
                caps["accuracy"] >= accuracy_requirement):
                
                cost = self.model_costs[model]
                estimated_cost = self._estimate_cost(cost, 1000, 500)  # Rough estimate
                
                if budget_limit is None or estimated_cost <= budget_limit:
                    suitable_models.append((model, estimated_cost, caps))
        
        # Sort by cost (ascending)
        suitable_models.sort(key=lambda x: x[1])
        
        if suitable_models:
            return suitable_models[0][0]  # Return cheapest suitable model
        else:
            return "gpt-3.5-turbo"  # Fallback
    
    def _estimate_cost(self, model_cost, input_tokens, output_tokens):
        """Estimate cost for a request."""
        input_cost = (input_tokens / 1000) * model_cost["input"]
        output_cost = (output_tokens / 1000) * model_cost["output"]
        return input_cost + output_cost

# Usage
selector = SmartModelSelector()

# For simple tasks
model = selector.select_model(
    task_complexity=2, 
    accuracy_requirement=6, 
    budget_limit=0.01
)
print(f"Selected model: {model}")

# For complex tasks requiring high accuracy
model = selector.select_model(
    task_complexity=8, 
    accuracy_requirement=9
)
print(f"Selected model: {model}")
```

### Batch Processing for Cost Efficiency

```python
class BatchProcessor:
    def __init__(self, batch_size=10, delay_seconds=1.0):
        self.batch_size = batch_size
        self.delay_seconds = delay_seconds
        self.pending_requests = []
        self.llm = BaseLLM()
    
    def add_request(self, message, callback=None, **kwargs):
        """Add request to batch queue."""
        request = {
            "message": message,
            "callback": callback,
            "kwargs": kwargs,
            "timestamp": time.time()
        }
        self.pending_requests.append(request)
        
        if len(self.pending_requests) >= self.batch_size:
            self._process_batch()
    
    def _process_batch(self):
        """Process accumulated requests as a batch."""
        if not self.pending_requests:
            return
        
        # Combine messages for batch processing
        combined_message = self._combine_messages(self.pending_requests)
        
        try:
            # Single API call for multiple requests
            response = self.llm.call(combined_message)
            responses = self._split_response(response, len(self.pending_requests))
            
            # Execute callbacks
            for request, response in zip(self.pending_requests, responses):
                if request["callback"]:
                    request["callback"](response)
            
        except Exception as e:
            print(f"Batch processing error: {e}")
            # Handle individual requests as fallback
            self._process_individually()
        
        self.pending_requests.clear()
    
    def _combine_messages(self, requests):
        """Combine multiple messages into one request."""
        messages = []
        for i, req in enumerate(requests):
            messages.append(f"Request {i+1}: {req['message']}")
        
        return "Process the following requests separately:\n\n" + "\n\n".join(messages)
    
    def _split_response(self, response, count):
        """Split combined response back into individual responses."""
        # Simple splitting logic - would need more sophisticated parsing
        parts = response.split(f"Response {i+1}:" for i in range(count))
        return [part.strip() for part in parts if part.strip()]
    
    def _process_individually(self):
        """Fallback to individual processing."""
        for request in self.pending_requests:
            try:
                response = self.llm.call(request["message"], **request["kwargs"])
                if request["callback"]:
                    request["callback"](response)
            except Exception as e:
                print(f"Individual request error: {e}")
    
    def flush(self):
        """Process remaining requests."""
        if self.pending_requests:
            self._process_batch()

# Usage
processor = BatchProcessor(batch_size=5)

def handle_response(response):
    print(f"Got response: {response[:50]}...")

# Add requests to batch
processor.add_request("What is AI?", handle_response)
processor.add_request("Explain machine learning", handle_response)
processor.add_request("Define neural networks", handle_response)

# Process remaining
processor.flush()
```

## Usage Analytics and Reporting

### Comprehensive Usage Analytics

```python
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

class UsageAnalytics:
    def __init__(self):
        self.usage_data = []
    
    def log_usage(self, model, input_tokens, output_tokens, cost, task_type=None):
        """Log API usage."""
        entry = {
            "timestamp": datetime.now(),
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
            "cost": cost,
            "task_type": task_type or "general"
        }
        self.usage_data.append(entry)
    
    def get_usage_dataframe(self):
        """Convert usage data to pandas DataFrame."""
        return pd.DataFrame(self.usage_data)
    
    def generate_report(self, days=30):
        """Generate comprehensive usage report."""
        df = self.get_usage_dataframe()
        if df.empty:
            return "No usage data available"
        
        # Filter by date range
        cutoff_date = datetime.now() - timedelta(days=days)
        df = df[df['timestamp'] >= cutoff_date]
        
        report = {
            "period": f"Last {days} days",
            "total_calls": len(df),
            "total_cost": df['cost'].sum(),
            "total_tokens": df['total_tokens'].sum(),
            "average_cost_per_call": df['cost'].mean(),
            "cost_by_model": df.groupby('model')['cost'].sum().to_dict(),
            "usage_by_task": df.groupby('task_type')['cost'].sum().to_dict(),
            "daily_usage": df.groupby(df['timestamp'].dt.date)['cost'].sum().to_dict()
        }
        
        return report
    
    def plot_usage_trends(self, metric="cost", days=30):
        """Plot usage trends."""
        df = self.get_usage_dataframe()
        if df.empty:
            print("No data to plot")
            return
        
        cutoff_date = datetime.now() - timedelta(days=days)
        df = df[df['timestamp'] >= cutoff_date]
        
        # Group by date
        daily_data = df.groupby(df['timestamp'].dt.date)[metric].sum()
        
        plt.figure(figsize=(12, 6))
        plt.plot(daily_data.index, daily_data.values, marker='o')
        plt.title(f"Daily {metric.title()} Trend")
        plt.xlabel("Date")
        plt.ylabel(metric.title())
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
    
    def cost_breakdown_pie(self):
        """Create pie chart of costs by model."""
        df = self.get_usage_dataframe()
        if df.empty:
            print("No data to plot")
            return
        
        model_costs = df.groupby('model')['cost'].sum()
        
        plt.figure(figsize=(10, 8))
        plt.pie(model_costs.values, labels=model_costs.index, autopct='%1.1f%%')
        plt.title("Cost Distribution by Model")
        plt.show()

# Usage
analytics = UsageAnalytics()

# Log usage (would be automated in real implementation)
analytics.log_usage("gpt-4", 1000, 500, 0.045, "analysis")
analytics.log_usage("gpt-3.5-turbo", 800, 200, 0.002, "simple_query")

# Generate reports
report = analytics.generate_report(days=7)
print(report)

# Create visualizations
analytics.plot_usage_trends("cost", days=7)
analytics.cost_breakdown_pie()
```

### Cost Prediction

```python
from sklearn.linear_model import LinearRegression
import numpy as np

class CostPredictor:
    def __init__(self):
        self.model = LinearRegression()
        self.is_trained = False
        self.usage_analytics = UsageAnalytics()
    
    def train(self, historical_data):
        """Train cost prediction model."""
        df = pd.DataFrame(historical_data)
        
        # Features: day of week, hour, input tokens, task type
        features = []
        targets = []
        
        for _, row in df.iterrows():
            day_of_week = row['timestamp'].weekday()
            hour = row['timestamp'].hour
            input_tokens = row['input_tokens']
            
            # One-hot encode task type (simplified)
            task_analysis = 1 if row['task_type'] == 'analysis' else 0
            task_generation = 1 if row['task_type'] == 'generation' else 0
            
            features.append([day_of_week, hour, input_tokens, task_analysis, task_generation])
            targets.append(row['cost'])
        
        X = np.array(features)
        y = np.array(targets)
        
        self.model.fit(X, y)
        self.is_trained = True
    
    def predict_cost(self, timestamp, input_tokens, task_type):
        """Predict cost for a future request."""
        if not self.is_trained:
            raise ValueError("Model not trained yet")
        
        day_of_week = timestamp.weekday()
        hour = timestamp.hour
        task_analysis = 1 if task_type == 'analysis' else 0
        task_generation = 1 if task_type == 'generation' else 0
        
        features = np.array([[day_of_week, hour, input_tokens, task_analysis, task_generation]])
        return self.model.predict(features)[0]
    
    def predict_daily_cost(self, date, expected_requests):
        """Predict total cost for a day."""
        total_predicted_cost = 0
        
        for req in expected_requests:
            timestamp = datetime.combine(date, datetime.min.time().replace(hour=req['hour']))
            cost = self.predict_cost(timestamp, req['input_tokens'], req['task_type'])
            total_predicted_cost += cost
        
        return total_predicted_cost

# Usage
predictor = CostPredictor()

# Train with historical data
historical_data = analytics.usage_data  # From analytics above
predictor.train(historical_data)

# Predict cost for future request
future_cost = predictor.predict_cost(
    timestamp=datetime.now() + timedelta(hours=1),
    input_tokens=1500,
    task_type='analysis'
)
print(f"Predicted cost: ${future_cost:.4f}")
```

## Integration with Monitoring Systems

### Prometheus Metrics

```python
from prometheus_client import Counter, Histogram, Gauge, start_http_server

class PrometheusLLMMetrics:
    def __init__(self):
        # Metrics
        self.api_calls_total = Counter(
            'llm_api_calls_total', 
            'Total LLM API calls',
            ['model', 'status']
        )
        
        self.api_cost_total = Counter(
            'llm_api_cost_total',
            'Total LLM API cost in USD'
        )
        
        self.api_duration = Histogram(
            'llm_api_duration_seconds',
            'LLM API call duration'
        )
        
        self.tokens_processed = Counter(
            'llm_tokens_processed_total',
            'Total tokens processed',
            ['type']  # input/output
        )
        
        self.active_requests = Gauge(
            'llm_active_requests',
            'Number of active LLM requests'
        )
    
    def record_api_call(self, model, status, duration, cost, input_tokens, output_tokens):
        """Record metrics for an API call."""
        self.api_calls_total.labels(model=model, status=status).inc()
        self.api_cost_total.inc(cost)
        self.api_duration.observe(duration)
        self.tokens_processed.labels(type='input').inc(input_tokens)
        self.tokens_processed.labels(type='output').inc(output_tokens)
    
    def start_metrics_server(self, port=8000):
        """Start Prometheus metrics server."""
        start_http_server(port)
        print(f"Metrics server started on port {port}")

# Usage
metrics = PrometheusLLMMetrics()
metrics.start_metrics_server()

# Record metrics
metrics.record_api_call(
    model="gpt-4",
    status="success",
    duration=2.5,
    cost=0.045,
    input_tokens=1000,
    output_tokens=500
)
```

## Best Practices Summary

1. **Set Clear Budgets**: Establish daily/monthly spending limits
2. **Monitor in Real-time**: Implement alerts for cost thresholds
3. **Choose Models Wisely**: Use the least expensive model that meets requirements
4. **Batch Similar Requests**: Reduce API calls through batching
5. **Cache Results**: Avoid duplicate calls for similar requests
6. **Track Usage Patterns**: Analyze trends to optimize future usage
7. **Implement Circuit Breakers**: Prevent runaway costs from failures
8. **Regular Reviews**: Conduct monthly cost reviews and optimizations

These pricing management strategies help ensure cost-effective use of AI models while maintaining application performance and reliability.