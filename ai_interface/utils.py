from __future__ import annotations

from wasabi import msg

def print_conversation(msgs):
    """
    Print the conversation in a readable format.

    Parameters:
    -----------
    msg: list
        The conversation messages to print.
    """
    for turn in msgs:
        icon = '🤖' if turn['role'] == 'assistant' else (
            '⚙️' if turn['role'] == 'system' else '👤'
        )
        msg.divider(icon)
        print(turn['content'])
