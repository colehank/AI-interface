# Troubleshooting

This guide covers common issues you might encounter when using LMITF and their solutions.

## Common Issues

### Authentication Errors

#### API Key Not Found

**Error:** `OpenAI API key not found`

**Cause:** Missing or incorrectly set API key

**Solutions:**

1. **Check Environment Variables**
   ```bash
   echo $OPENAI_API_KEY
   ```

2. **Set Environment Variable**
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```

3. **Use .env File**
   ```env
   # .env
   OPENAI_API_KEY=your-api-key-here
   OPENAI_BASE_URL=https://api.openai.com/v1
   ```

4. **Manual Configuration**
   ```python
   from lmitf import BaseLLM
   
   # Explicit configuration
   llm = BaseLLM(api_key="your-api-key")
   ```

#### Invalid API Key

**Error:** `401 Unauthorized`

**Cause:** Invalid or expired API key

**Solutions:**

1. **Verify Key Format**
   - OpenAI keys start with `sk-`
   - Check for extra spaces or characters

2. **Test Key Directly**
   ```python
   import openai
   client = openai.OpenAI(api_key="your-key")
   try:
       client.models.list()
       print("✅ API key is valid")
   except Exception as e:
       print(f"❌ API key error: {e}")
   ```

3. **Generate New Key**
   - Go to OpenAI dashboard
   - Create new API key
   - Update your configuration

### Connection Issues

#### Network Connectivity

**Error:** `Connection timeout` or `Connection refused`

**Cause:** Network issues or firewall blocking

**Solutions:**

1. **Check Internet Connection**
   ```bash
   ping api.openai.com
   ```

2. **Test HTTPS Connectivity**
   ```bash
   curl -I https://api.openai.com/v1/models
   ```

3. **Configure Proxy (if needed)**
   ```python
   import os
   os.environ["HTTP_PROXY"] = "http://proxy.company.com:8080"
   os.environ["HTTPS_PROXY"] = "https://proxy.company.com:8080"
   ```

4. **Custom Base URL**
   ```python
   llm = BaseLLM(base_url="https://your-custom-endpoint.com/v1")
   ```

#### Rate Limiting

**Error:** `429 Too Many Requests`

**Cause:** Exceeded API rate limits

**Solutions:**

1. **Implement Retry Logic**
   ```python
   import time
   import random
   
   def api_call_with_retry(llm, message, max_retries=3):
       for attempt in range(max_retries):
           try:
               return llm.call(message)
           except Exception as e:
               if "429" in str(e) and attempt < max_retries - 1:
                   delay = (2 ** attempt) + random.uniform(0, 1)
                   print(f"Rate limit hit, waiting {delay:.2f}s...")
                   time.sleep(delay)
               else:
                   raise e
   ```

2. **Add Delays Between Calls**
   ```python
   import time
   
   responses = []
   for message in messages:
       response = llm.call(message)
       responses.append(response)
       time.sleep(1)  # 1 second delay
   ```

3. **Check Rate Limits**
   ```python
   # Monitor response headers for rate limit info
   # This would require custom implementation
   ```

### Model Issues

#### Model Not Available

**Error:** `Model not found` or `Invalid model`

**Cause:** Using non-existent or deprecated model

**Solutions:**

1. **List Available Models**
   ```python
   import openai
   client = openai.OpenAI()
   models = client.models.list()
   for model in models.data:
       print(model.id)
   ```

2. **Use Supported Models**
   ```python
   # Common working models
   supported_models = [
       "gpt-4o",
       "gpt-4o-mini", 
       "gpt-4",
       "gpt-3.5-turbo"
   ]
   
   llm = BaseLLM()
   response = llm.call("Hello", model="gpt-4o")
   ```

3. **Model Fallback**
   ```python
   def call_with_fallback(llm, message, models=None):
       if models is None:
           models = ["gpt-4o", "gpt-4", "gpt-3.5-turbo"]
       
       for model in models:
           try:
               return llm.call(message, model=model)
           except Exception as e:
               print(f"Model {model} failed: {e}")
               continue
       
       raise Exception("All models failed")
   ```

#### Token Limit Exceeded

**Error:** `Token limit exceeded` or `Context length exceeded`

**Cause:** Input too long for model's context window

**Solutions:**

1. **Check Token Count**
   ```python
   import tiktoken
   
   def count_tokens(text, model="gpt-4"):
       encoding = tiktoken.encoding_for_model(model)
       return len(encoding.encode(text))
   
   token_count = count_tokens("Your long text here")
   print(f"Token count: {token_count}")
   ```

2. **Truncate Input**
   ```python
   def truncate_text(text, max_tokens=4000, model="gpt-4"):
       encoding = tiktoken.encoding_for_model(model)
       tokens = encoding.encode(text)
       
       if len(tokens) <= max_tokens:
           return text
       
       truncated_tokens = tokens[:max_tokens]
       return encoding.decode(truncated_tokens)
   
   truncated = truncate_text("Very long text...", max_tokens=3000)
   response = llm.call(truncated)
   ```

3. **Chunk Large Inputs**
   ```python
   def process_in_chunks(llm, text, chunk_size=3000):
       chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
       responses = []
       
       for i, chunk in enumerate(chunks):
           prompt = f"Process this chunk ({i+1}/{len(chunks)}):\n\n{chunk}"
           response = llm.call(prompt)
           responses.append(response)
       
       return responses
   ```

### Vision Model Issues

#### Image Format Not Supported

**Error:** `Unsupported image format`

**Cause:** Using unsupported image format

**Solutions:**

1. **Convert Image Format**
   ```python
   from PIL import Image
   
   def convert_to_supported_format(image_path, output_path=None):
       """Convert image to supported format (PNG/JPEG)."""
       img = Image.open(image_path)
       
       if output_path is None:
           output_path = image_path.rsplit('.', 1)[0] + '.png'
       
       img.save(output_path, 'PNG')
       return output_path
   
   # Usage
   converted_path = convert_to_supported_format("image.webp")
   response = lvm.call("Describe this image", image_path=converted_path)
   ```

2. **Check Supported Formats**
   ```python
   supported_formats = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
   
   def is_supported_format(file_path):
       return any(file_path.lower().endswith(fmt) for fmt in supported_formats)
   ```

#### Image Too Large

**Error:** `Image file too large`

**Cause:** Image exceeds size limits

**Solutions:**

1. **Resize Image**
   ```python
   from PIL import Image
   
   def resize_image(image_path, max_size=(1024, 1024)):
       """Resize image while maintaining aspect ratio."""
       img = Image.open(image_path)
       img.thumbnail(max_size, Image.Resampling.LANCZOS)
       
       output_path = image_path.rsplit('.', 1)[0] + '_resized.png'
       img.save(output_path, 'PNG')
       return output_path
   
   resized_path = resize_image("large_image.jpg")
   response = lvm.call("Analyze this", image_path=resized_path)
   ```

2. **Compress Image**
   ```python
   def compress_image(image_path, quality=85):
       """Compress JPEG image."""
       img = Image.open(image_path)
       output_path = image_path.rsplit('.', 1)[0] + '_compressed.jpg'
       img.save(output_path, 'JPEG', quality=quality, optimize=True)
       return output_path
   ```

### Template Issues

#### Template File Not Found

**Error:** `Template file not found`

**Cause:** Incorrect template path

**Solutions:**

1. **Check File Path**
   ```python
   import os
   
   template_path = "path/to/template.py"
   if os.path.exists(template_path):
       print("✅ Template file exists")
   else:
       print("❌ Template file not found")
       # List files in directory
       directory = os.path.dirname(template_path)
       files = os.listdir(directory)
       print(f"Files in {directory}: {files}")
   ```

2. **Use Absolute Paths**
   ```python
   import os
   from lmitf import TemplateLLM
   
   # Convert to absolute path
   template_path = os.path.abspath("templates/my_template.py")
   template_llm = TemplateLLM(template_path)
   ```

#### Template Syntax Error

**Error:** `Template syntax error` or `Python syntax error`

**Cause:** Invalid Python syntax in template file

**Solutions:**

1. **Validate Template Syntax**
   ```python
   import ast
   
   def validate_template_syntax(template_path):
       """Check if template file has valid Python syntax."""
       try:
           with open(template_path, 'r') as f:
               content = f.read()
           ast.parse(content)
           print("✅ Template syntax is valid")
           return True
       except SyntaxError as e:
           print(f"❌ Syntax error in template: {e}")
           return False
   
   validate_template_syntax("template.py")
   ```

2. **Test Template Loading**
   ```python
   import importlib.util
   
   def test_template_import(template_path):
       """Test if template can be imported."""
       try:
           spec = importlib.util.spec_from_file_location("test_template", template_path)
           module = importlib.util.module_from_spec(spec)
           spec.loader.exec_module(module)
           
           # Check for required attributes
           if hasattr(module, 'template'):
               print("✅ Template loaded successfully")
           else:
               print("❌ Template missing 'template' variable")
               
       except Exception as e:
           print(f"❌ Template import error: {e}")
   ```

## Debugging Tools

### Enable Debug Logging

```python
import logging
from lmitf import BaseLLM

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

llm = BaseLLM()
response = llm.call("Hello world")
```

### Request/Response Inspection

```python
class DebugLLM(BaseLLM):
    def call(self, messages, **kwargs):
        print(f"🔍 Request: {messages}")
        print(f"🔍 Parameters: {kwargs}")
        
        try:
            response = super().call(messages, **kwargs)
            print(f"✅ Response: {response[:100]}...")
            return response
        except Exception as e:
            print(f"❌ Error: {e}")
            raise e

# Usage
debug_llm = DebugLLM()
response = debug_llm.call("Test message")
```

### Health Check Function

```python
def health_check():
    """Comprehensive LMITF health check."""
    print("🏥 LMITF Health Check")
    print("=" * 30)
    
    # Check environment variables
    import os
    api_key = os.getenv('OPENAI_API_KEY')
    base_url = os.getenv('OPENAI_BASE_URL')
    
    print(f"API Key: {'✅ Set' if api_key else '❌ Missing'}")
    print(f"Base URL: {base_url or 'Default'}")
    
    # Test API connection
    try:
        llm = BaseLLM()
        response = llm.call("test", max_tokens=1)
        print("✅ API Connection: Working")
    except Exception as e:
        print(f"❌ API Connection: {e}")
    
    # Test vision model (if applicable)
    try:
        from lmitf import BaseLVM
        lvm = BaseLVM()
        print("✅ Vision Model: Available")
    except Exception as e:
        print(f"❌ Vision Model: {e}")
    
    print("\n🎯 Health check complete")

# Run health check
health_check()
```

## Performance Issues

### Slow Response Times

**Symptoms:** API calls taking longer than expected

**Solutions:**

1. **Check Model Selection**
   ```python
   # Faster models
   fast_models = ["gpt-3.5-turbo", "gpt-4o-mini"]
   response = llm.call("Quick question", model="gpt-3.5-turbo")
   ```

2. **Reduce Token Count**
   ```python
   # Shorter prompts = faster responses
   response = llm.call("Summarize: AI is...", max_tokens=100)
   ```

3. **Use Streaming**
   ```python
   # Start processing immediately
   for chunk in llm.call("Long task", stream=True):
       process_chunk(chunk)
   ```

### Memory Issues

**Symptoms:** High memory usage or out of memory errors

**Solutions:**

1. **Clear Call History**
   ```python
   llm = BaseLLM()
   # After many calls
   llm.call_history.clear()  # Free memory
   ```

2. **Process in Batches**
   ```python
   def process_large_dataset(items, batch_size=100):
       for i in range(0, len(items), batch_size):
           batch = items[i:i+batch_size]
           process_batch(batch)
           # Memory is freed between batches
   ```

## Getting Help

### Collect Diagnostic Information

```python
def collect_diagnostics():
    """Collect system information for troubleshooting."""
    import sys
    import platform
    import lmitf
    
    info = {
        "lmitf_version": lmitf.__version__,
        "python_version": sys.version,
        "platform": platform.platform(),
        "environment_vars": {
            "OPENAI_API_KEY": "Set" if os.getenv('OPENAI_API_KEY') else "Missing",
            "OPENAI_BASE_URL": os.getenv('OPENAI_BASE_URL', "Default")
        }
    }
    
    return info

# Share this info when reporting issues
diagnostics = collect_diagnostics()
print(diagnostics)
```

### Where to Get Help

1. **GitHub Issues**: [https://github.com/colehank/AI-interface/issues](https://github.com/colehank/AI-interface/issues)
2. **Documentation**: Check the [API reference](api/llm.md) and [examples](examples.md)
3. **Community**: Search for similar issues in the repository

### Reporting Bugs

When reporting bugs, include:

1. **LMITF version**
2. **Python version**
3. **Operating system**
4. **Minimal code example**
5. **Full error message**
6. **Expected vs actual behavior**

This troubleshooting guide should help resolve most common issues with LMITF. If you encounter issues not covered here, please report them on GitHub.