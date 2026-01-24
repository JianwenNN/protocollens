"""
Prompts package for ProtocolLens.

This package contains prompt generation and boundary detection logic.
"""

from .role_specific_qa import get_role_specific_qa_prompt, get_role_description
from .boundary_detection import (
    is_unsupported_question,
    get_unsupported_message,
    get_supported_question_examples,
    get_unsupported_question_examples
)

__all__ = [
    'get_role_specific_qa_prompt',
    'get_role_description',
    'is_unsupported_question',
    'get_unsupported_message',
    'get_supported_question_examples',
    'get_unsupported_question_examples'
]
