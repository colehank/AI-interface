from __future__ import annotations

import base64
import io
import os
from unittest.mock import MagicMock
from unittest.mock import Mock
from unittest.mock import patch

import pytest
from openai import OpenAI
from PIL import Image

from lmitf.base_lvm import AgentLVM
from lmitf.base_lvm import BaseLVM


class TestBaseLVM:
    def setup_method(self):
        """Setup test fixtures"""
        self.mock_api_key = 'test-api-key'
        self.mock_base_url = 'https://test.openai.com'

    @patch.dict(os.environ, {'OPENAI_API_KEY': 'env-api-key', 'OPENAI_BASE_URL': 'https://env.openai.com'})
    @patch('lmitf.base_lvm.OpenAI')
    def test_init_with_env_vars(self, mock_openai):
        """Test initialization with environment variables"""
        lvm = BaseLVM()
        mock_openai.assert_called_once_with(
            api_key='env-api-key',
            base_url='https://env.openai.com',
        )

    @patch('lmitf.base_lvm.OpenAI')
    def test_init_with_params(self, mock_openai):
        """Test initialization with explicit parameters"""
        lvm = BaseLVM(api_key=self.mock_api_key, base_url=self.mock_base_url)
        mock_openai.assert_called_once_with(
            api_key=self.mock_api_key,
            base_url=self.mock_base_url,
        )

    @patch('lmitf.base_lvm.OpenAI')
    def test_create_image(self, mock_openai):
        """Test image creation"""
        # Create a test image
        test_image = Image.new('RGB', (100, 100), color='red')
        img_buffer = io.BytesIO()
        test_image.save(img_buffer, format='PNG')
        test_b64 = base64.b64encode(img_buffer.getvalue()).decode()

        mock_client = Mock()
        mock_response = Mock()
        mock_response.data = [Mock()]
        mock_response.data[0].b64_json = test_b64
        mock_client.images.generate.return_value = mock_response
        mock_openai.return_value = mock_client

        lvm = BaseLVM(api_key=self.mock_api_key)
        result = lvm.create('A beautiful landscape')

        assert isinstance(result, Image.Image)
        mock_client.images.generate.assert_called_once_with(
            model='gpt-image-1',
            prompt='A beautiful landscape',
            size='1024x1024',
        )

    @patch('lmitf.base_lvm.OpenAI')
    def test_edit_image_without_mask(self, mock_openai):
        """Test image editing without mask"""
        # Create test images
        original_image = Image.new('RGB', (100, 100), color='blue')
        edited_image = Image.new('RGB', (100, 100), color='green')

        img_buffer = io.BytesIO()
        edited_image.save(img_buffer, format='PNG')
        edited_b64 = base64.b64encode(img_buffer.getvalue()).decode()

        mock_client = Mock()
        mock_response = Mock()
        mock_response.data = [Mock()]
        mock_response.data[0].b64_json = edited_b64
        mock_client.images.edit.return_value = mock_response
        mock_openai.return_value = mock_client

        lvm = BaseLVM(api_key=self.mock_api_key)
        result = lvm.edit(original_image, 'Make it greener')

        assert isinstance(result, Image.Image)
        mock_client.images.edit.assert_called_once()

    @patch('lmitf.base_lvm.OpenAI')
    def test_edit_image_with_mask(self, mock_openai):
        """Test image editing with mask"""
        original_image = Image.new('RGB', (100, 100), color='blue')
        mask_image = Image.new('RGB', (100, 100), color='white')
        edited_image = Image.new('RGB', (100, 100), color='green')

        img_buffer = io.BytesIO()
        edited_image.save(img_buffer, format='PNG')
        edited_b64 = base64.b64encode(img_buffer.getvalue()).decode()

        mock_client = Mock()
        mock_response = Mock()
        mock_response.data = [Mock()]
        mock_response.data[0].b64_json = edited_b64
        mock_client.images.edit.return_value = mock_response
        mock_openai.return_value = mock_client

        lvm = BaseLVM(api_key=self.mock_api_key)
        result = lvm.edit(original_image, 'Make it greener', mask=mask_image)

        assert isinstance(result, Image.Image)
        mock_client.images.edit.assert_called_once()


class TestAgentLVM:
    def setup_method(self):
        """Setup test fixtures"""
        self.mock_api_key = 'test-api-key'
        self.mock_base_url = 'https://test.openai.com'

    @patch('lmitf.base_lvm.OpenAI')
    def test_init(self, mock_openai):
        """Test AgentLVM initialization"""
        agent = AgentLVM(api_key=self.mock_api_key, base_url=self.mock_base_url)
        mock_openai.assert_called_once_with(
            api_key=self.mock_api_key,
            base_url=self.mock_base_url,
        )

    def test_encode_decode_image(self):
        """Test image encoding and decoding"""
        agent = AgentLVM(api_key=self.mock_api_key)

        # Create test image
        test_image = Image.new('RGB', (50, 50), color='red')

        # Test encoding
        encoded = agent._encode_img(test_image)
        assert isinstance(encoded, str)

        # Test decoding
        decoded = agent._decode_img(encoded)
        assert isinstance(decoded, Image.Image)
        assert decoded.size == (50, 50)

    @patch('lmitf.base_lvm.OpenAI')
    def test_create_with_agent(self, mock_openai):
        """Test image creation with agent"""
        test_image = Image.new('RGB', (100, 100), color='blue')
        img_buffer = io.BytesIO()
        test_image.save(img_buffer, format='PNG')
        test_b64 = base64.b64encode(img_buffer.getvalue()).decode()

        mock_client = Mock()
        mock_response = Mock()
        mock_response.output = [Mock()]
        mock_response.output[0].type = 'image_generation_call'
        mock_response.output[0].result = test_b64
        mock_client.responses.create.return_value = mock_response
        mock_openai.return_value = mock_client

        agent = AgentLVM(api_key=self.mock_api_key)
        messages = [
            {'role': 'system', 'content': 'You are a helpful assistant'},
            {'role': 'user', 'content': 'Create an image of a mountain'},
        ]
        result = agent.create(messages)

        assert isinstance(result, Image.Image)
        mock_client.responses.create.assert_called_once()

    @patch('lmitf.base_lvm.OpenAI')
    def test_create_no_image_data(self, mock_openai):
        """Test create method when no image data is returned"""
        mock_client = Mock()

        # Create a mock response where output is empty list (no image generation calls)
        mock_response = Mock()
        mock_response.output = []  # Empty list means no image generation calls

        # But we also need output.content for the error message
        # So we need output to be both iterable and have a content attribute
        class MockOutput:
            def __init__(self):
                self.content = 'Error occurred'
            def __iter__(self):
                return iter([])  # Return empty iterator

        mock_response.output = MockOutput()

        mock_client.responses.create.return_value = mock_response
        mock_openai.return_value = mock_client

        agent = AgentLVM(api_key=self.mock_api_key)
        messages = [{'role': 'user', 'content': 'Create an image'}]

        with pytest.raises(ValueError, match='Error occurred'):
            agent.create(messages)

    @patch('lmitf.base_lvm.OpenAI')
    def test_edit_single_image(self, mock_openai):
        """Test editing a single image with agent"""
        input_image = Image.new('RGB', (100, 100), color='red')
        output_image = Image.new('RGB', (100, 100), color='blue')

        img_buffer = io.BytesIO()
        output_image.save(img_buffer, format='PNG')
        output_b64 = base64.b64encode(img_buffer.getvalue()).decode()

        mock_client = Mock()
        mock_response = Mock()
        mock_response.output = [Mock()]
        mock_response.output[0].type = 'image_generation_call'
        mock_response.output[0].result = output_b64
        mock_client.responses.create.return_value = mock_response
        mock_openai.return_value = mock_client

        agent = AgentLVM(api_key=self.mock_api_key)
        result = agent.edit('Make it blue', input_image)

        assert isinstance(result, Image.Image)
        mock_client.responses.create.assert_called_once()

    @patch('lmitf.base_lvm.OpenAI')
    def test_edit_multiple_images(self, mock_openai):
        """Test editing multiple images with agent"""
        input_images = [
            Image.new('RGB', (100, 100), color='red'),
            Image.new('RGB', (100, 100), color='green'),
        ]
        output_image = Image.new('RGB', (100, 100), color='blue')

        img_buffer = io.BytesIO()
        output_image.save(img_buffer, format='PNG')
        output_b64 = base64.b64encode(img_buffer.getvalue()).decode()

        mock_client = Mock()
        mock_response = Mock()
        mock_response.output = [Mock()]
        mock_response.output[0].type = 'image_generation_call'
        mock_response.output[0].result = output_b64
        mock_client.responses.create.return_value = mock_response
        mock_openai.return_value = mock_client

        agent = AgentLVM(api_key=self.mock_api_key)
        result = agent.edit('Combine these images', input_images)

        assert isinstance(result, Image.Image)
        mock_client.responses.create.assert_called_once()

    @patch('lmitf.base_lvm.OpenAI')
    def test_edit_no_image_data(self, mock_openai):
        """Test edit method when no image data is returned"""
        input_image = Image.new('RGB', (100, 100), color='red')

        mock_client = Mock()

        # Create a mock response where output is empty list (no image generation calls)
        mock_response = Mock()

        # But we also need output.content for the error message
        # So we need output to be both iterable and have a content attribute
        class MockOutput:
            def __init__(self):
                self.content = 'Error occurred'
            def __iter__(self):
                return iter([])  # Return empty iterator

        mock_response.output = MockOutput()

        mock_client.responses.create.return_value = mock_response
        mock_openai.return_value = mock_client

        agent = AgentLVM(api_key=self.mock_api_key)

        with pytest.raises(ValueError, match='Error occurred'):
            agent.edit('Edit this', input_image)
