"""
utils.py — Tibby Chatbot Utility Functions
Response formatting and input validation helpers.
"""

import random
from typing import Tuple

from config import (
    PERSONALITY_EMOJIS,
    CLOSING_PHRASES,
    MAX_INPUT_LENGTH,
    MIN_INPUT_LENGTH,
)

# Prefixes that indicate the response already has personality applied
_PERSONALITY_PREFIXES = tuple(PERSONALITY_EMOJIS + ["⚠️", "❌"])


def format_response(text: str, add_personality: bool = True) -> str:
    """
    Optionally prepend a personality emoji and append a closing phrase.

    Skips decoration if the text already starts with a known emoji prefix
    (avoids double-decorating error messages or pre-formatted replies).
    """
    if add_personality and not text.startswith(_PERSONALITY_PREFIXES):
        emoji = random.choice(PERSONALITY_EMOJIS)
        closing = random.choice(CLOSING_PHRASES)
        return f"{emoji} {text} {closing}"
    return text


def validate_input(message: str) -> Tuple[bool, str]:
    """
    Validate user-supplied message text.

    Returns:
        (True, "") on success, or (False, error_string) on failure.
    """
    if not message or not message.strip():
        return (False, "⚠️ Please provide a message.")

    if len(message) > MAX_INPUT_LENGTH:
        return (
            False,
            f"⚠️ Message too long. Please keep it under {MAX_INPUT_LENGTH} characters.",
        )

    if len(message.strip()) < MIN_INPUT_LENGTH:
        return (False, "⚠️ Message too short. Please provide a valid question.")

    return (True, "")
