# Utils API Reference

```{eval-rst}
.. automodule:: lmitf.utils
   :members:
   :undoc-members:
   :show-inheritance:
```

## Overview

The utils module provides utility functions for common tasks when working with LMITF, including conversation formatting, data processing, and helper functions.

## Function Reference

### print_conversation()

```{eval-rst}
.. autofunction:: lmitf.utils.print_conversation
```

A utility function to display conversation messages in a readable format with visual icons.

**Parameters:**
- `msgs` (list): List of conversation messages in OpenAI format

**Usage:**

```python
from lmitf.utils import print_conversation

# Format: [{"role": "user", "content": "Hello"}, {"role": "assistant", "content": "Hi there!"}]
conversation = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What's the weather like today?"},
    {"role": "assistant", "content": "I don't have access to real-time weather data, but I can help you find weather information."},
    {"role": "user", "content": "How can I check the weather?"}
]

print_conversation(conversation)
```

**Output:**
```
⚙️ ════════════════════════════════════════════════════════════════════════════════
You are a helpful assistant.

👤 ════════════════════════════════════════════════════════════════════════════════
What's the weather like today?

🤖 ════════════════════════════════════════════════════════════════════════════════
I don't have access to real-time weather data, but I can help you find weather information.

👤 ════════════════════════════════════════════════════════════════════════════════
How can I check the weather?
```

## Icon Legend

- 🤖 **Assistant**: Messages from the AI assistant
- 👤 **User**: Messages from the user
- ⚙️ **System**: System messages and prompts

## Integration with BaseLLM

The utils module integrates seamlessly with LMITF classes:

```python
from lmitf import BaseLLM
from lmitf.utils import print_conversation

llm = BaseLLM()

# Build a conversation
messages = [
    {"role": "system", "content": "You are a coding assistant."},
    {"role": "user", "content": "How do I create a Python list?"}
]

# Get response
response = llm.call(messages)

# Add response to conversation
messages.append({"role": "assistant", "content": response})

# Display the full conversation nicely
print_conversation(messages)
```

## Alternative Import

The `print_conversation` function is also available as `print_turn` in the main module:

```python
from lmitf import print_turn

# These are equivalent
print_turn(messages)
print_conversation(messages)
```

## Custom Formatting

For custom conversation formatting, you can extend the function:

```python
from wasabi import msg

def custom_print_conversation(msgs, show_timestamps=False):
    """Custom conversation printer with optional timestamps."""
    import datetime
    
    for i, turn in enumerate(msgs):
        icon = '🤖' if turn['role'] == 'assistant' else (
            '⚙️' if turn['role'] == 'system' else '👤'
        )
        
        header = f"{icon} Turn {i+1}"
        if show_timestamps:
            header += f" ({datetime.datetime.now().strftime('%H:%M:%S')})"
            
        msg.divider(header)
        print(turn['content'])
        print()  # Extra spacing

# Usage
custom_print_conversation(messages, show_timestamps=True)
```

## Best Practices

1. **Debug Conversations**: Use `print_conversation()` to debug multi-turn conversations
2. **Log Interactions**: Capture conversation flows for analysis
3. **User Interface**: Display conversations in CLI applications
4. **Development**: Monitor conversation state during development

## Future Utilities

The utils module may be extended with additional helper functions:

- Message validation
- Token counting utilities  
- Conversation saving/loading
- Format conversion helpers

## Related Functions

- `lmitf.BaseLLM.call()` - Generate responses that can be formatted
- `lmitf.BaseLVM.call()` - Vision model responses for formatting