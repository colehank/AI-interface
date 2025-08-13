from __future__ import annotations

import os
import tempfile
from string import Template
from unittest.mock import MagicMock
from unittest.mock import Mock
from unittest.mock import patch

import pytest

from lmitf.base_llm import BaseLLM
from lmitf.templete_llm import TemplateLLM


class TestTemplateLLM:
    def setup_method(self):
        """Setup test fixtures"""
        self.mock_api_key = 'test-api-key'
        self.mock_base_url = 'https://test.openai.com'

        # Create a temporary template file for testing
        self.template_content = '''
from __future__ import annotations

prompt_template = [
    {'role': 'system', 'content': 'You are a helpful assistant.'},
    {'role': 'user', 'content': ''}
]

conditioned_frame = """
Please process the following:
Name: $name
Age: $age
Task: $task
"""
'''

    def create_temp_template(self, content=None):
        """Create a temporary template file"""
        if content is None:
            content = self.template_content

        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(content)
            return f.name

    def teardown_method(self):
        """Clean up temporary files"""
        # Clean up any temporary files if they exist
        pass

    @patch('lmitf.templete_llm.BaseLLM.__init__')
    def test_init_success(self, mock_base_init):
        """Test successful initialization"""
        mock_base_init.return_value = None
        template_path = self.create_temp_template()

        try:
            with patch('lmitf.templete_llm.msg.text'):
                template_llm = TemplateLLM(template_path, api_key=self.mock_api_key)

            assert template_llm.template_path == template_path
            assert set(template_llm.variables) == {'name', 'age', 'task'}
            assert isinstance(template_llm.template_obj, Template)
        finally:
            os.unlink(template_path)

    def test_init_nonexistent_file(self):
        """Test initialization with non-existent file"""
        with pytest.raises(AssertionError, match='Template file does not exist'):
            TemplateLLM('/nonexistent/path.py')

    def test_init_non_python_file(self):
        """Test initialization with non-Python file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write('test content')
            temp_path = f.name

        try:
            with pytest.raises(AssertionError, match='Template file must be a Python file'):
                TemplateLLM(temp_path)
        finally:
            os.unlink(temp_path)

    def test_load_template_missing_prompt_template(self):
        """Test loading template without prompt_template"""
        content = '''
conditioned_frame = "Test: $test"
'''
        template_path = self.create_temp_template(content)

        try:
            with pytest.raises(AttributeError, match="Template module must define 'prompt_template'"):
                TemplateLLM(template_path)
        finally:
            os.unlink(template_path)

    def test_load_template_missing_conditioned_frame(self):
        """Test loading template without conditioned_frame"""
        content = '''
prompt_template = [{'role': 'system', 'content': 'test'}]
'''
        template_path = self.create_temp_template(content)

        try:
            with pytest.raises(AttributeError, match="Template module must define 'conditioned_frame'"):
                TemplateLLM(template_path)
        finally:
            os.unlink(template_path)

    def test_load_template_no_variables(self):
        """Test loading template with no variables in conditioned_frame"""
        content = '''
prompt_template = [{'role': 'system', 'content': 'test'}]
conditioned_frame = "No variables here"
'''
        template_path = self.create_temp_template(content)

        try:
            with pytest.raises(ValueError, match='No variables found in conditioned_frame'):
                TemplateLLM(template_path)
        finally:
            os.unlink(template_path)

    @patch('lmitf.templete_llm.BaseLLM.__init__')
    def test_fill_success(self, mock_base_init):
        """Test successful template filling"""
        mock_base_init.return_value = None
        template_path = self.create_temp_template()

        try:
            with patch('lmitf.templete_llm.msg.text'):
                template_llm = TemplateLLM(template_path)

            result = template_llm._fill(name='John', age='30', task='coding')

            assert len(result) == 2
            assert result[0]['role'] == 'system'
            assert result[1]['role'] == 'user'
            assert 'Name: John' in result[1]['content']
            assert 'Age: 30' in result[1]['content']
            assert 'Task: coding' in result[1]['content']
        finally:
            os.unlink(template_path)

    @patch('lmitf.templete_llm.BaseLLM.__init__')
    def test_fill_missing_variables(self, mock_base_init):
        """Test template filling with missing variables"""
        mock_base_init.return_value = None
        template_path = self.create_temp_template()

        try:
            with patch('lmitf.templete_llm.msg.text'):
                template_llm = TemplateLLM(template_path)

            with pytest.raises(ValueError, match='Missing required variables'):
                template_llm._fill(name='John')  # Missing age and task
        finally:
            os.unlink(template_path)

    @patch('lmitf.templete_llm.BaseLLM.__init__')
    def test_fill_extra_variables(self, mock_base_init):
        """Test template filling with extra variables"""
        mock_base_init.return_value = None
        template_path = self.create_temp_template()

        try:
            with patch('lmitf.templete_llm.msg.text'):
                template_llm = TemplateLLM(template_path)

            with pytest.raises(ValueError, match='Unexpected variables provided'):
                template_llm._fill(name='John', age='30', task='coding', extra='variable')
        finally:
            os.unlink(template_path)

    @patch('lmitf.templete_llm.BaseLLM.call')
    @patch('lmitf.templete_llm.BaseLLM.__init__')
    def test_call_success(self, mock_base_init, mock_base_call):
        """Test successful template LLM call"""
        mock_base_init.return_value = None
        mock_base_call.return_value = 'Template response'
        template_path = self.create_temp_template()

        try:
            with patch('lmitf.templete_llm.msg.text'):
                template_llm = TemplateLLM(template_path)

            result = template_llm.call(
                name='John',
                age='30',
                task='coding',
                model='gpt-4',
                temperature=0.7,
            )

            assert result == 'Template response'
            mock_base_call.assert_called_once()

            # Check that messages were properly filled and other params passed through
            call_kwargs = mock_base_call.call_args[1]
            assert 'messages' in call_kwargs
            assert call_kwargs['model'] == 'gpt-4'
            assert call_kwargs['temperature'] == 0.7
        finally:
            os.unlink(template_path)

    @patch('lmitf.templete_llm.BaseLLM.__init__')
    def test_call_no_template(self, mock_base_init):
        """Test call when prompt_template is not defined"""
        mock_base_init.return_value = None
        template_path = self.create_temp_template()

        try:
            with patch('lmitf.templete_llm.msg.text'):
                template_llm = TemplateLLM(template_path)
                template_llm.prompt_template = None  # Simulate missing template

            with pytest.raises(ValueError, match='Prompt template is not defined'):
                template_llm.call(name='John', age='30', task='coding')
        finally:
            os.unlink(template_path)

    @patch('lmitf.templete_llm.BaseLLM.__init__')
    @patch('lmitf.templete_llm.pd.DataFrame')
    def test_repr_html(self, mock_dataframe, mock_base_init):
        """Test HTML representation"""
        mock_base_init.return_value = None
        mock_df = Mock()
        mock_df.T._repr_html_.return_value = '<table>test</table>'
        mock_dataframe.return_value = mock_df

        template_path = self.create_temp_template()

        try:
            with patch('lmitf.templete_llm.msg.text'):
                template_llm = TemplateLLM(template_path)

            result = template_llm._repr_html_()

            assert result == '<table>test</table>'
            mock_dataframe.assert_called_once()

            # Check DataFrame data
            call_args = mock_dataframe.call_args[0][0]
            assert 'Name' in call_args
            assert 'Variables to fill' in call_args
        finally:
            os.unlink(template_path)

    def test_load_template_import_error(self):
        """Test handling of import errors in template module"""
        content = '''
import nonexistent_module  # This will cause ImportError
prompt_template = []
conditioned_frame = "$test"
'''
        template_path = self.create_temp_template(content)

        try:
            with pytest.raises(ImportError, match='Failed to load template module'):
                TemplateLLM(template_path)
        finally:
            os.unlink(template_path)


class TestTemplateLLMIntegration:
    """Integration tests for TemplateLLM with real template files"""

    @patch('lmitf.templete_llm.BaseLLM.__init__')
    def test_real_template_integration(self, mock_base_init):
        """Test with a realistic template structure"""
        mock_base_init.return_value = None

        template_content = '''
from __future__ import annotations

prompt_template = [
    {"role": "system", "content": "You are an expert data analyst."},
    {"role": "user", "content": "Analyze the following data and provide insights."},
    {"role": "user", "content": ""}
]

conditioned_frame = """
Dataset: $dataset_name
Columns: $columns
Sample Data: $sample_data
Analysis Type: $analysis_type
"""
'''

        template_path = None
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(template_content)
                template_path = f.name

            with patch('lmitf.templete_llm.msg.text'):
                template_llm = TemplateLLM(template_path)

            assert len(template_llm.variables) == 4
            assert 'dataset_name' in template_llm.variables

        finally:
            if template_path and os.path.exists(template_path):
                os.unlink(template_path)
