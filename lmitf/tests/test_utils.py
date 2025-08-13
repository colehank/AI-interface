from __future__ import annotations

import os
from unittest.mock import Mock
from unittest.mock import patch

import pytest

from lmitf.utils import print_conversation


class TestPrintConversation:
    def setup_method(self):
        """Setup test fixtures"""
        self.sample_conversation = [
            {'role': 'system', 'content': 'You are a helpful assistant.'},
            {'role': 'user', 'content': 'Hello, how are you?'},
            {'role': 'assistant', 'content': 'I am doing well, thank you for asking!'},
            {'role': 'user', 'content': 'What is the weather like?'},
            {'role': 'assistant', 'content': 'I do not have access to real-time weather data.'},
        ]

    @patch('lmitf.utils.msg.divider')
    @patch('builtins.print')
    def test_print_conversation_basic(self, mock_print, mock_divider):
        """Test basic conversation printing"""
        print_conversation(self.sample_conversation)

        # Check that divider was called for each message
        assert mock_divider.call_count == len(self.sample_conversation)

        # Check that print was called for each message content
        assert mock_print.call_count == len(self.sample_conversation)

        # Verify the correct icons were used
        expected_calls = ['⚙️', '👤', '🤖', '👤', '🤖']
        actual_calls = [call[0][0] for call in mock_divider.call_args_list]
        assert actual_calls == expected_calls

    @patch('lmitf.utils.msg.divider')
    @patch('builtins.print')
    def test_print_conversation_empty_list(self, mock_print, mock_divider):
        """Test printing empty conversation list"""
        print_conversation([])

        mock_divider.assert_not_called()
        mock_print.assert_not_called()

    @patch('lmitf.utils.msg.divider')
    @patch('builtins.print')
    def test_print_conversation_single_message(self, mock_print, mock_divider):
        """Test printing single message"""
        single_message = [{'role': 'user', 'content': 'Single message'}]
        print_conversation(single_message)

        mock_divider.assert_called_once_with('👤')
        mock_print.assert_called_once_with('Single message')

    @patch('lmitf.utils.msg.divider')
    @patch('builtins.print')
    def test_print_conversation_system_message(self, mock_print, mock_divider):
        """Test printing system message uses correct icon"""
        system_message = [{'role': 'system', 'content': 'System prompt'}]
        print_conversation(system_message)

        mock_divider.assert_called_once_with('⚙️')
        mock_print.assert_called_once_with('System prompt')

    @patch('lmitf.utils.msg.divider')
    @patch('builtins.print')
    def test_print_conversation_assistant_message(self, mock_print, mock_divider):
        """Test printing assistant message uses correct icon"""
        assistant_message = [{'role': 'assistant', 'content': 'AI response'}]
        print_conversation(assistant_message)

        mock_divider.assert_called_once_with('🤖')
        mock_print.assert_called_once_with('AI response')

    @patch('lmitf.utils.msg.divider')
    @patch('builtins.print')
    def test_print_conversation_user_message(self, mock_print, mock_divider):
        """Test printing user message uses correct icon"""
        user_message = [{'role': 'user', 'content': 'User question'}]
        print_conversation(user_message)

        mock_divider.assert_called_once_with('👤')
        mock_print.assert_called_once_with('User question')

    @patch('lmitf.utils.msg.divider')
    @patch('builtins.print')
    def test_print_conversation_unknown_role(self, mock_print, mock_divider):
        """Test printing message with unknown role defaults to user icon"""
        unknown_role_message = [{'role': 'unknown', 'content': 'Unknown role'}]
        print_conversation(unknown_role_message)

        mock_divider.assert_called_once_with('👤')
        mock_print.assert_called_once_with('Unknown role')

    @patch('lmitf.utils.msg.divider')
    @patch('builtins.print')
    def test_print_conversation_multiple_roles(self, mock_print, mock_divider):
        """Test printing conversation with all role types"""
        mixed_conversation = [
            {'role': 'system', 'content': 'System'},
            {'role': 'assistant', 'content': 'Assistant'},
            {'role': 'user', 'content': 'User'},
            {'role': 'unknown', 'content': 'Unknown'},
        ]

        print_conversation(mixed_conversation)

        expected_icons = ['⚙️', '🤖', '👤', '👤']
        actual_icons = [call[0][0] for call in mock_divider.call_args_list]
        assert actual_icons == expected_icons

        expected_contents = ['System', 'Assistant', 'User', 'Unknown']
        actual_contents = [call[0][0] for call in mock_print.call_args_list]
        assert actual_contents == expected_contents

    @patch('lmitf.utils.msg.divider')
    @patch('builtins.print')
    def test_print_conversation_content_types(self, mock_print, mock_divider):
        """Test printing different types of content"""
        various_content = [
            {'role': 'user', 'content': 'String content'},
            {'role': 'user', 'content': ''},  # Empty string
            {'role': 'user', 'content': 'Multi\nline\ncontent'},  # Multi-line
            {'role': 'user', 'content': '🔥 Emoji content 🚀'},  # With emojis
        ]

        print_conversation(various_content)

        expected_contents = [
            'String content',
            '',
            'Multi\nline\ncontent',
            '🔥 Emoji content 🚀',
        ]
        actual_contents = [call[0][0] for call in mock_print.call_args_list]
        assert actual_contents == expected_contents

    @patch('lmitf.utils.msg.divider')
    @patch('builtins.print')
    def test_print_conversation_malformed_messages(self, mock_print, mock_divider):
        """Test handling of malformed message dictionaries"""
        malformed_messages = [
            {'role': 'user', 'content': 'Good message'},
            {'role': 'user'},  # Missing content
            {'content': 'Missing role'},  # Missing role
            {},  # Empty dict
        ]

        # Should not raise exception but may behave differently
        # The actual behavior depends on implementation details
        try:
            print_conversation(malformed_messages)
            # If it doesn't crash, that's good
        except (KeyError, AttributeError):
            # These are expected for malformed messages
            pass


class TestUtilsIntegration:
    """Integration tests for utils module functions"""

    @patch('lmitf.utils.msg')
    def test_import_and_basic_functionality(self, mock_msg):
        """Test that the module imports correctly and basic functionality works"""
        from lmitf.utils import print_conversation

        # Verify function exists and is callable
        assert callable(print_conversation)

        # Test with a simple conversation
        conversation = [
            {'role': 'user', 'content': 'Test message'},
        ]

        # Should not raise any exceptions
        print_conversation(conversation)
