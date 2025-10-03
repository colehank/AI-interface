"""Large Model Interface - A flexible interface for interacting with large language models and vision models."""
from __future__ import annotations

import os
import os.path as op

from .base_llm import BaseLLM
from .base_lvm import BaseLVM
from .datasets import manager as prompts
from .templete_llm import TemplateLLM
from .utils import print_conversation as print_turn
from .agent_llm import AgentLLM

__version__ = '0.1.22'
__description__ = 'Large Model Interface - A flexible interface for interacting with large language models and vision models.'
