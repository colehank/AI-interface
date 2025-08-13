from __future__ import annotations

import os
from unittest.mock import Mock
from unittest.mock import patch

import pytest

from lmitf.datasets.manager import llm_prompts
from lmitf.datasets.manager import lvm_prompts


class TestDatasetManager:
    def setup_method(self):
        """Setup test fixtures"""
        pass

    def test_llm_prompts_structure(self):
        """Test that llm_prompts is a dictionary with proper structure"""
        assert isinstance(llm_prompts, dict)

        # Check that all values are absolute paths
        for name, path in llm_prompts.items():
            assert isinstance(name, str)
            assert isinstance(path, str)
            assert os.path.isabs(path), f'Path {path} is not absolute'
            assert path.endswith('.py'), f'Path {path} does not end with .py'

    def test_lvm_prompts_structure(self):
        """Test that lvm_prompts is a dictionary with proper structure"""
        assert isinstance(lvm_prompts, dict)

        # Check that all values are absolute paths
        for name, path in lvm_prompts.items():
            assert isinstance(name, str)
            assert isinstance(path, str)
            assert os.path.isabs(path), f'Path {path} is not absolute'
            assert path.endswith('.py'), f'Path {path} does not end with .py'

    @patch('lmitf.datasets.manager.os.listdir')
    @patch('lmitf.datasets.manager.op.exists')
    @patch('lmitf.datasets.manager.op.dirname')
    def test_llm_prompts_filtering(self, mock_dirname, mock_exists, mock_listdir):
        """Test that only .py files are included in llm_prompts"""
        # Setup mocks
        mock_dirname.return_value = '/test/datasets'
        mock_listdir.return_value = [
            'template1.py',
            'template2.py',
            'readme.txt',
            'config.json',
            'template3.py',
        ]

        # Re-import to trigger the module-level code with mocks
        import importlib
        import lmitf.datasets.manager
        importlib.reload(lmitf.datasets.manager)

        # Should only include .py files
        expected_py_files = {'template1', 'template2', 'template3'}
        actual_keys = set(lmitf.datasets.manager.llm_prompts.keys())

        # All keys should correspond to .py files (without extension)
        for key in actual_keys:
            assert key + '.py' in mock_listdir.return_value

    def test_prompt_name_extraction(self):
        """Test that prompt names are correctly extracted from file names"""
        # This tests the actual implementation
        for name in llm_prompts.keys():
            # Names should not contain file extensions
            assert not name.endswith('.py')
            # Names should be valid Python identifiers (mostly)
            assert isinstance(name, str)
            assert len(name) > 0

    def test_paths_point_to_existing_files(self):
        """Test that all paths in the dictionaries point to existing files"""
        # Test LLM prompts
        for name, path in llm_prompts.items():
            assert os.path.exists(path), f'LLM prompt file {path} does not exist'
            assert os.path.isfile(path), f'LLM prompt path {path} is not a file'

        # Test LVM prompts
        for name, path in lvm_prompts.items():
            assert os.path.exists(path), f'LVM prompt file {path} does not exist'
            assert os.path.isfile(path), f'LVM prompt path {path} is not a file'

    def test_no_duplicate_names(self):
        """Test that there are no duplicate names in the dictionaries"""
        llm_names = list(llm_prompts.keys())
        lvm_names = list(lvm_prompts.keys())

        # Check for duplicates within each dictionary
        assert len(llm_names) == len(set(llm_names)), 'Duplicate names in llm_prompts'
        assert len(lvm_names) == len(set(lvm_names)), 'Duplicate names in lvm_prompts'

    def test_known_prompts_exist(self):
        """Test that known prompt templates exist"""
        # We know text2triples should exist based on the file structure
        assert 'text2triples' in llm_prompts

        # The path should contain the expected filename
        text2triples_path = llm_prompts['text2triples']
        assert 'text2triples.py' in text2triples_path

    @patch('lmitf.datasets.manager.op.join')
    @patch('lmitf.datasets.manager.op.abspath')
    @patch('lmitf.datasets.manager.op.dirname')
    @patch('lmitf.datasets.manager.os.listdir')
    def test_path_construction(self, mock_listdir, mock_dirname, mock_abspath, mock_join):
        """Test that paths are constructed correctly"""
        # Setup mocks
        mock_dirname.return_value = '/base/datasets'
        mock_listdir.return_value = ['test.py']
        mock_join.return_value = '/base/datasets/llm_prompts/test.py'
        mock_abspath.return_value = '/abs/base/datasets/llm_prompts/test.py'

        # Re-import to trigger path construction
        import importlib
        import lmitf.datasets.manager
        importlib.reload(lmitf.datasets.manager)

        # Verify that join and abspath were called properly
        mock_join.assert_called()
        mock_abspath.assert_called()

    def test_module_level_variables_are_accessible(self):
        """Test that module-level variables are properly accessible"""
        from lmitf.datasets import manager

        # Should be able to access the dictionaries directly
        assert hasattr(manager, 'llm_prompts')
        assert hasattr(manager, 'lvm_prompts')

        # Check that they are dictionaries with proper structure
        assert isinstance(manager.llm_prompts, dict)
        assert isinstance(manager.lvm_prompts, dict)


class TestManagerIntegration:
    """Integration tests for the manager module"""

    def test_can_import_template_files(self):
        """Test that we can actually import the template files referenced in the manager"""
        import importlib.util

        # Try to import each LLM prompt template
        for name, path in llm_prompts.items():
            if os.path.exists(path):
                try:
                    spec = importlib.util.spec_from_file_location(f'test_{name}', path)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    # Basic validation that it looks like a prompt template
                    # (This is a basic sanity check)
                    assert hasattr(module, 'prompt_template') or hasattr(module, 'conditioned_frame')

                except Exception as e:
                    pytest.fail(f'Could not import template {name} from {path}: {e}')

    def test_template_files_have_expected_attributes(self):
        """Test that template files have the expected structure"""
        import importlib.util

        for name, path in llm_prompts.items():
            if os.path.exists(path):
                spec = importlib.util.spec_from_file_location(f'test_{name}', path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Check for expected attributes that TemplateLLM would use
                has_prompt_template = hasattr(module, 'prompt_template')
                has_conditioned_frame = hasattr(module, 'conditioned_frame')

                # At least one should be present for a valid template
                assert has_prompt_template or has_conditioned_frame, \
                    f'Template {name} missing required attributes'

    def test_manager_integration_with_templating(self):
        """Test that the manager works well with the templating system"""
        # This is more of an integration test to ensure manager and template system work together
        if 'text2triples' in llm_prompts:
            template_path = llm_prompts['text2triples']

            # Verify we can load this with TemplateLLM (mock the actual LLM calls)
            with patch('lmitf.templete_llm.BaseLLM.__init__', return_value=None):
                with patch('lmitf.templete_llm.msg.text'):
                    from lmitf.templete_llm import TemplateLLM
                    template_llm = TemplateLLM(template_path)

                    # Should have loaded successfully
                    assert template_llm.template_path == template_path
                    assert hasattr(template_llm, 'variables')
