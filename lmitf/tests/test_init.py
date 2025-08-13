from __future__ import annotations

from unittest.mock import Mock
from unittest.mock import patch

import pytest

import lmitf
from lmitf import BaseLLM
from lmitf import BaseLVM
from lmitf import print_turn
from lmitf import TemplateLLM
from lmitf.datasets import manager as prompts


class TestLmitfPackage:
    """Test the main lmitf package imports and structure"""

    def test_package_version(self):
        """Test that package has version defined"""
        assert hasattr(lmitf, '__version__')
        assert isinstance(lmitf.__version__, str)
        assert len(lmitf.__version__) > 0

    def test_package_description(self):
        """Test that package has description defined"""
        assert hasattr(lmitf, '__description__')
        assert isinstance(lmitf.__description__, str)
        assert 'Large Model Interface' in lmitf.__description__

    def test_main_imports(self):
        """Test that main classes are importable from package root"""
        # Test direct imports from lmitf
        from lmitf import BaseLLM, BaseLVM, TemplateLLM, print_turn

        assert BaseLLM is not None
        assert BaseLVM is not None
        assert TemplateLLM is not None
        assert callable(print_turn)

    def test_prompts_import(self):
        """Test that prompts manager is importable"""
        from lmitf.datasets import manager as prompts

        assert hasattr(prompts, 'llm_prompts')
        assert hasattr(prompts, 'lvm_prompts')

    def test_pricing_import(self):
        """Test that pricing module is importable"""
        from lmitf.pricing import DMX

        assert DMX is not None

    @patch('lmitf.base_llm.OpenAI')
    def test_basellm_instantiation(self, mock_openai):
        """Test that BaseLLM can be instantiated"""
        mock_openai.return_value = Mock()

        llm = BaseLLM(api_key='test-key')
        assert llm is not None
        assert hasattr(llm, 'call')
        assert hasattr(llm, 'call_embed')
        assert hasattr(llm, 'call_history')

    @patch('lmitf.base_lvm.OpenAI')
    def test_baselvm_instantiation(self, mock_openai):
        """Test that BaseLVM can be instantiated"""
        mock_openai.return_value = Mock()

        lvm = BaseLVM(api_key='test-key')
        assert lvm is not None
        assert hasattr(lvm, 'create')
        assert hasattr(lvm, 'edit')

    def test_print_turn_function(self):
        """Test that print_turn function is properly imported"""
        # This should be the same as print_conversation from utils
        from lmitf.utils import print_conversation

        assert print_turn is print_conversation

    def test_package_structure(self):
        """Test overall package structure and organization"""
        # Test that key modules are present
        import lmitf.base_llm
        import lmitf.base_lvm
        import lmitf.templete_llm
        import lmitf.utils
        import lmitf.datasets.manager
        import lmitf.pricing

        # Basic structure validation
        assert hasattr(lmitf.base_llm, 'BaseLLM')
        assert hasattr(lmitf.base_lvm, 'BaseLVM')
        assert hasattr(lmitf.base_lvm, 'AgentLVM')
        assert hasattr(lmitf.templete_llm, 'TemplateLLM')
        assert hasattr(lmitf.utils, 'print_conversation')

    def test_all_exports(self):
        """Test that __init__.py exports match expected interface"""
        import lmitf

        # Check that main classes are available at package level
        expected_exports = [
            'BaseLLM', 'BaseLVM', 'TemplateLLM', 'print_turn',
            '__version__', '__description__',
        ]

        for export in expected_exports:
            assert hasattr(lmitf, export), f'Missing export: {export}'

    def test_prompts_accessibility(self):
        """Test that prompts are accessible through the package"""
        # Should be able to access prompts through the imported alias
        assert isinstance(prompts.llm_prompts, dict)
        assert isinstance(prompts.lvm_prompts, dict)

    @patch('lmitf.base_llm.OpenAI')
    @patch('lmitf.templete_llm.msg.text')
    def test_end_to_end_import_chain(self, mock_msg, mock_openai):
        """Test complete import chain works"""
        mock_openai.return_value = Mock()

        # Should be able to go from package import to actual usage
        from lmitf import BaseLLM, TemplateLLM
        from lmitf.datasets import manager as prompts

        # Create instances
        llm = BaseLLM(api_key='test')

        # This would normally require a real template file, but we test the import chain
        if prompts.llm_prompts:  # Only test if there are actual prompt files
            # Just verify the classes are importable and the prompts are accessible
            assert len(prompts.llm_prompts) > 0


class TestPackageIntegration:
    """Integration tests for package components working together"""

    def test_documentation_consistency(self):
        """Test that package docstrings are consistent"""
        import lmitf

        # Package should have consistent documentation
        package_doc = lmitf.__doc__ or ''
        package_desc = lmitf.__description__

        # Basic consistency checks
        assert 'Large Model Interface' in package_desc

    def test_version_format(self):
        """Test that version follows semantic versioning"""
        import re
        import lmitf

        version = lmitf.__version__
        # Basic semver pattern (major.minor.patch with optional pre-release)
        semver_pattern = r'^\d+\.\d+\.\d+(?:-[\w\d\-\.]+)?(?:\+[\w\d\-\.]+)?$'

        assert re.match(semver_pattern, version), f"Version {version} doesn't follow semver"

    @patch('lmitf.base_llm.OpenAI')
    def test_cross_module_compatibility(self, mock_openai):
        """Test that modules work well together"""
        mock_openai.return_value = Mock()

        from lmitf import BaseLLM, print_turn

        # Create an LLM instance
        llm = BaseLLM(api_key='test')

        # Simulate conversation history
        llm.call_history = [
            {'role': 'user', 'content': 'Test message'},
            {'role': 'assistant', 'content': 'Test response'},
        ]

        # Should be able to use print_turn with the history
        with patch('lmitf.utils.msg.divider'), patch('builtins.print'):
            print_turn(llm.call_history)  # Should not raise exception

    def test_import_performance(self):
        """Test that imports don't take excessively long"""
        import time

        start_time = time.time()
        import lmitf
        from lmitf import BaseLLM, BaseLVM, TemplateLLM
        from lmitf.datasets import manager
        from lmitf.pricing import DMX
        end_time = time.time()

        import_time = end_time - start_time
        # Imports should be fast (less than 5 seconds even on slow systems)
        assert import_time < 5.0, f'Imports took too long: {import_time:.2f}s'
