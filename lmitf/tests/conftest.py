from __future__ import annotations

import pytest


def pytest_configure(config):
    """Configure pytest with custom markers and settings"""
    config.addinivalue_line(
        'markers', 'unit: mark test as a unit test',
    )
    config.addinivalue_line(
        'markers', 'integration: mark test as an integration test',
    )
    config.addinivalue_line(
        'markers', 'slow: mark test as slow running',
    )
    config.addinivalue_line(
        'markers', 'network: mark test as requiring network access',
    )


@pytest.fixture
def mock_openai_client():
    """Fixture providing a mock OpenAI client"""
    from unittest.mock import Mock

    mock_client = Mock()
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = 'Test response'
    mock_client.chat.completions.create.return_value = mock_response

    return mock_client


@pytest.fixture
def mock_embedding_response():
    """Fixture providing a mock embedding response"""
    from unittest.mock import Mock

    mock_response = Mock()
    mock_response.data = [Mock()]
    mock_response.data[0].embedding = [0.1, 0.2, 0.3, 0.4, 0.5]

    return mock_response


@pytest.fixture
def sample_conversation():
    """Fixture providing a sample conversation for testing"""
    return [
        {'role': 'system', 'content': 'You are a helpful assistant.'},
        {'role': 'user', 'content': 'Hello, how are you?'},
        {'role': 'assistant', 'content': 'I am doing well, thank you!'},
        {'role': 'user', 'content': 'Can you help me with Python?'},
        {'role': 'assistant', 'content': 'Of course! I would be happy to help.'},
    ]


@pytest.fixture
def temp_template_file(tmp_path):
    """Fixture providing a temporary template file"""
    template_content = '''
from __future__ import annotations

prompt_template = [
    {'role': 'system', 'content': 'You are a helpful assistant.'},
    {'role': 'user', 'content': ''}
]

conditioned_frame = """
Please help with the following:
Topic: $topic
Question: $question
Context: $context
"""
'''

    template_file = tmp_path / 'test_template.py'
    template_file.write_text(template_content)

    return str(template_file)


@pytest.fixture
def mock_pricing_data():
    """Fixture providing mock pricing API data"""
    return {
        'data': {
            'model_info': '[["gpt-4", {"supplier": "OpenAI", "tags": ["premium"], "illustrate": "Advanced model"}], ["gpt-3.5-turbo", {"supplier": "OpenAI", "tags": ["standard"], "illustrate": "Fast model"}]]',
            'model_group': {
                'default': {
                    'GroupRatio': 1.0,
                    'ModelPrice': {
                        'gpt-4': {'isPrice': False, 'price': 30.0},
                        'gpt-3.5-turbo': {'isPrice': False, 'price': 2.0},
                    },
                },
            },
            'model_completion_ratio': {
                'gpt-4': 2.0,
                'gpt-3.5-turbo': 1.5,
            },
        },
    }


@pytest.fixture
def mock_image():
    """Fixture providing a mock PIL Image"""
    from PIL import Image

    # Create a simple test image
    return Image.new('RGB', (100, 100), color='red')


@pytest.fixture
def mock_image_b64():
    """Fixture providing base64 encoded image data"""
    from PIL import Image
    import io
    import base64

    # Create test image and encode it
    img = Image.new('RGB', (50, 50), color='blue')
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)

    return base64.b64encode(buffer.read()).decode('utf-8')


# Custom pytest markers for better test organization
# pytestmark = pytest.mark.unit  # Commented out to avoid warning


def pytest_collection_modifyitems(config, items):
    """Automatically mark tests based on their location and content"""
    for item in items:
        # Mark integration tests
        if 'integration' in item.name.lower() or 'test_integration' in str(item.fspath):
            item.add_marker(pytest.mark.integration)

        # Mark network tests
        if any(keyword in item.name.lower() for keyword in ['network', 'api', 'http', 'request']):
            item.add_marker(pytest.mark.network)

        # Mark slow tests
        if any(keyword in item.name.lower() for keyword in ['slow', 'performance', 'large', 'timeout']):
            item.add_marker(pytest.mark.slow)


@pytest.fixture(scope='session')
def test_data_dir(tmp_path_factory):
    """Session-scoped fixture for test data directory"""
    return tmp_path_factory.mktemp('test_data')


# Environment setup for tests
@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch):
    """Automatically setup test environment for all tests"""
    # Set test environment variables
    monkeypatch.setenv('OPENAI_API_KEY', 'test-api-key-for-testing')
    monkeypatch.setenv('OPENAI_BASE_URL', 'https://test.openai.com')

    # Ensure we don't accidentally make real API calls during testing
    monkeypatch.setenv('PYTEST_RUNNING', 'true')
