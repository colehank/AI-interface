"""
Test configuration and requirements for lmitf package tests.

This file contains pytest configuration, fixtures, and test requirements
to ensure comprehensive testing of the lmitf package functionality.
"""
# Test Requirements
from __future__ import annotations
REQUIRED_PACKAGES = [
    'pytest>=7.0.0',
    'pytest-cov>=4.0.0',
    'pytest-mock>=3.10.0',
    'requests-mock>=1.10.0',
    'pillow>=9.0.0',
    'pandas>=1.5.0',
]

# Test Coverage Requirements
MINIMUM_COVERAGE = 85  # Minimum 85% test coverage

# Test Categories
TEST_CATEGORIES = {
    'unit': 'Unit tests for individual components',
    'integration': 'Integration tests for component interaction',
    'edge_cases': 'Edge cases and error handling tests',
    'performance': 'Performance and load tests',
    'regression': 'Regression tests for bug fixes',
}

# Test Execution Guidelines
TEST_GUIDELINES = """
1. Run all tests: pytest
2. Run with coverage: pytest --cov=lmitf --cov-report=html
3. Run specific category: pytest -m unit
4. Run excluding network tests: pytest -m "not network"
5. Verbose output: pytest -v
6. Stop on first failure: pytest -x
"""

# Mocking Guidelines
MOCKING_GUIDELINES = """
1. Always mock external API calls (OpenAI, DMX API, etc.)
2. Mock file I/O operations in unit tests
3. Use fixtures for common mock objects
4. Ensure mocks return realistic data structures
5. Test both success and failure scenarios
"""

# Test File Organization
TEST_STRUCTURE = {
    'test_llm.py': 'Tests for BaseLLM class and LLM functionality',
    'test_lvm.py': 'Tests for BaseLVM and AgentLVM classes',
    'test_price.py': 'Tests for pricing/DMX API functionality',
    'test_template_llm.py': 'Tests for TemplateLLM class',
    'test_utils.py': 'Tests for utility functions',
    'test_manager.py': 'Tests for dataset manager',
    'test_init.py': 'Tests for package initialization',
    'test_edge_cases.py': 'Edge cases and error handling tests',
    'conftest.py': 'pytest configuration and fixtures',
}

if __name__ == '__main__':
    print('LMITF Test Suite Configuration')
    print('=' * 40)
    print(f"Required packages: {', '.join(REQUIRED_PACKAGES)}")
    print(f'Minimum coverage: {MINIMUM_COVERAGE}%')
    print('\nTest Categories:')
    for category, description in TEST_CATEGORIES.items():
        print(f'  {category}: {description}')
    print(f'\nTest Execution:\n{TEST_GUIDELINES}')
    print(f'\nMocking Guidelines:\n{MOCKING_GUIDELINES}')
