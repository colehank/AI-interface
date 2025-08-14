# Contributing to LMITF

We welcome contributions to LMITF! This guide will help you get started with contributing to the project.

## Getting Started

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/your-username/AI-interface.git
   cd AI-interface
   ```

### Development Setup

1. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -e .  # Install in development mode
   ```

3. **Install Development Tools**
   ```bash
   pip install pytest black isort mypy flake8
   ```

## Development Workflow

### Code Style

We use standard Python tools for code formatting and linting:

```bash
# Format code
black lmitf/
isort lmitf/

# Check formatting
black --check lmitf/
isort --check-only lmitf/

# Lint code
flake8 lmitf/
mypy lmitf/
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest lmitf/tests/test_llm.py

# Run with coverage
pytest --cov=lmitf
```

### Making Changes

1. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Your Changes**
   - Write code following existing patterns
   - Add tests for new functionality
   - Update documentation as needed

3. **Test Your Changes**
   ```bash
   pytest
   black --check lmitf/
   flake8 lmitf/
   ```

4. **Commit Changes**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

## Types of Contributions

### Bug Reports

When reporting bugs, please include:

- **Description**: Clear description of the bug
- **Steps to Reproduce**: Minimal code example
- **Expected Behavior**: What should happen
- **Actual Behavior**: What actually happens  
- **Environment**: Python version, OS, LMITF version

### Feature Requests

For new features, please provide:

- **Use Case**: Why is this feature needed?
- **Proposed Solution**: How should it work?
- **Alternatives**: Any alternative approaches considered?

### Code Contributions

#### Adding New Features

1. **Discuss First**: Open an issue to discuss major features
2. **Follow Patterns**: Look at existing code for patterns
3. **Add Tests**: All new code should have tests
4. **Update Docs**: Update documentation for user-facing changes

#### Example: Adding a New Method

```python
# In lmitf/base_llm.py
class BaseLLM:
    def call_with_system(self, system_message: str, user_message: str, **kwargs):
        """
        Make a call with a system message and user message.
        
        Parameters
        ----------
        system_message : str
            System prompt to set context
        user_message : str
            User's message
        **kwargs
            Additional parameters for the API call
            
        Returns
        -------
        str
            The model's response
        """
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
        return self.call(messages, **kwargs)
```

#### Adding Tests

```python
# In lmitf/tests/test_llm.py
def test_call_with_system():
    """Test call_with_system method."""
    llm = BaseLLM()
    
    # Mock the underlying call method
    with patch.object(llm, 'call', return_value="Test response") as mock_call:
        response = llm.call_with_system("You are helpful", "Hello")
        
        # Verify the call was made with correct messages
        expected_messages = [
            {"role": "system", "content": "You are helpful"},
            {"role": "user", "content": "Hello"}
        ]
        mock_call.assert_called_once_with(expected_messages)
        
        assert response == "Test response"
```

### Documentation Contributions

Documentation improvements are always welcome:

- Fix typos or unclear explanations
- Add more examples
- Improve API documentation
- Create tutorials for new features

## Code Guidelines

### Python Style

- Follow PEP 8
- Use type hints where appropriate
- Write docstrings for all public functions/classes
- Keep functions focused and small

### Docstring Format

Use NumPy-style docstrings:

```python
def example_function(param1: str, param2: int = 10) -> str:
    """
    Brief description of the function.

    Longer description if needed, explaining what the function does,
    any important details, etc.

    Parameters
    ----------
    param1 : str
        Description of param1
    param2 : int, optional
        Description of param2, by default 10

    Returns
    -------
    str
        Description of return value

    Raises
    ------
    ValueError
        When param1 is empty
        
    Examples
    --------
    >>> result = example_function("hello", 5)
    >>> print(result)
    hello processed 5 times
    """
    if not param1:
        raise ValueError("param1 cannot be empty")
    return f"{param1} processed {param2} times"
```

### Error Handling

- Use specific exception types
- Provide helpful error messages
- Handle edge cases gracefully

```python
def safe_api_call(self, message: str, **kwargs):
    """Make API call with proper error handling."""
    if not message.strip():
        raise ValueError("Message cannot be empty")
    
    try:
        return self.client.chat.completions.create(
            messages=[{"role": "user", "content": message}],
            **kwargs
        )
    except openai.RateLimitError as e:
        raise RuntimeError(f"Rate limit exceeded: {e}")
    except openai.APIError as e:
        raise RuntimeError(f"API error: {e}")
```

## Testing Guidelines

### Test Structure

```python
import pytest
from unittest.mock import patch, MagicMock
from lmitf import BaseLLM

class TestBaseLLM:
    """Test cases for BaseLLM class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.llm = BaseLLM()
    
    def test_basic_functionality(self):
        """Test basic functionality."""
        # Test implementation
        pass
    
    def test_error_handling(self):
        """Test error handling."""
        # Test error cases
        pass
    
    @pytest.mark.parametrize("input_val,expected", [
        ("hello", "HELLO"),
        ("world", "WORLD"),
    ])
    def test_with_parameters(self, input_val, expected):
        """Test with different parameters."""
        result = some_function(input_val)
        assert result == expected
```

### Mocking External Services

```python
@patch('lmitf.base_llm.OpenAI')
def test_api_call(self, mock_openai):
    """Test API call with mocked client."""
    # Set up mock
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "Test response"
    mock_client.chat.completions.create.return_value = mock_response
    mock_openai.return_value = mock_client
    
    # Test
    llm = BaseLLM()
    response = llm.call("Test message")
    
    # Verify
    assert response == "Test response"
    mock_client.chat.completions.create.assert_called_once()
```

## Submitting Pull Requests

### Before Submitting

1. **Run All Checks**
   ```bash
   pytest
   black --check lmitf/
   isort --check-only lmitf/
   flake8 lmitf/
   mypy lmitf/
   ```

2. **Update Documentation**
   - Update docstrings
   - Add examples if applicable
   - Update CHANGELOG.md

3. **Test Edge Cases**
   - Test with different Python versions if possible
   - Test error conditions
   - Test with different configurations

### Pull Request Template

```markdown
## Description
Brief description of the changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] Added tests for new functionality
- [ ] Manual testing completed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
```

### Review Process

1. **Automated Checks**: CI will run tests and linting
2. **Code Review**: Maintainers will review your code
3. **Feedback**: Address any requested changes
4. **Merge**: Once approved, your PR will be merged

## Release Process

### Versioning

We follow semantic versioning (SemVer):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Changelog

Update `CHANGELOG.md` with your changes:

```markdown
## [Unreleased]

### Added
- New feature description

### Changed
- Changed behavior description

### Fixed
- Bug fix description
```

## Community Guidelines

### Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help newcomers learn
- Celebrate diverse perspectives

### Communication

- **Issues**: For bug reports and feature requests
- **Discussions**: For questions and general discussion
- **Pull Requests**: For code contributions

## Recognition

Contributors are recognized in several ways:

- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- GitHub contributor statistics
- Special recognition for significant contributions

## Getting Help

If you need help contributing:

1. **Read the Documentation**: Start with this guide and the API docs
2. **Check Existing Issues**: Look for similar questions
3. **Ask Questions**: Open a discussion or issue
4. **Join the Community**: Connect with other contributors

Thank you for contributing to LMITF! Your contributions help make the library better for everyone.