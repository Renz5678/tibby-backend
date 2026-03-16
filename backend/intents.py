"""
intents.py — Tibby Chatbot Intent Engine
Loads intents.json and matches user messages via exact/fuzzy logic.
"""

import json
import random
import difflib
from typing import Any, Dict, Optional, Tuple

from config import (
    INTENTS_FILE,
    CONFIDENCE_THRESHOLD,
    FUZZY_MATCH_CUTOFF,
    MAX_PATTERNS_TO_CHECK,
)


# ==============================
# Load Intents
# ==============================
def load_intents() -> Dict[str, Any]:
    """Load intents from JSON file with graceful error handling."""
    try:
        with open(INTENTS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        count = len(data.get("intents", []))
        print(f"✅ intents.json loaded successfully ({count} intents)")
        return data
    except FileNotFoundError:
        print("⚠️ intents.json not found — chatbot will use fallback replies only")
        return {"intents": []}
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing intents.json: {e}")
        return {"intents": []}


# Module-level singletons
intents_data: Dict[str, Any] = load_intents()
_intent_match_cache: Dict[str, Tuple[Optional[Dict], float]] = {}


# ==============================
# Intent Matching
# ==============================
def match_intent(user_message: str) -> Tuple[Optional[str], float]:
    """
    Match a user message against loaded intent patterns.

    Strategy (fastest-first):
      1. Exact substring match → score 1.0, return immediately
      2. Fuzzy SequenceMatcher ratio above FUZZY_MATCH_CUTOFF
      3. Return best score ≥ CONFIDENCE_THRESHOLD or (None, 0.0)

    Results are cached to avoid re-processing identical messages.

    Returns:
        (response_text, confidence) or (None, 0.0) when no match found.
    """
    normalized = user_message.lower().strip()

    # Cache hit
    if normalized in _intent_match_cache:
        cached_intent, cached_score = _intent_match_cache[normalized]
        if cached_intent:
            responses = cached_intent.get("responses", [])
            return (random.choice(responses), cached_score) if responses else (None, 0.0)
        return (None, 0.0)

    best_match: Optional[Dict] = None
    best_score: float = 0.0
    best_response: Optional[str] = None
    patterns_checked = 0

    for intent in intents_data.get("intents", []):
        patterns = intent.get("patterns", [])
        responses = intent.get("responses", [])

        if not patterns or not responses:
            continue

        for pattern in patterns:
            if patterns_checked >= MAX_PATTERNS_TO_CHECK:
                break
            patterns_checked += 1

            pattern_norm = pattern.lower().strip()

            # Exact substring → perfect match, cache & return immediately
            if pattern_norm in normalized:
                _intent_match_cache[normalized] = (intent, 1.0)
                return (random.choice(responses), 1.0)

            # Fuzzy match
            score = difflib.SequenceMatcher(None, normalized, pattern_norm).ratio()
            if score > best_score and score >= FUZZY_MATCH_CUTOFF:
                best_score = score
                best_match = intent
                best_response = random.choice(responses)

    # Cache result (even negative results to avoid re-checking)
    if best_score >= CONFIDENCE_THRESHOLD:
        _intent_match_cache[normalized] = (best_match, best_score)
        return (best_response, best_score)

    _intent_match_cache[normalized] = (None, 0.0)
    return (None, 0.0)


def clear_intent_cache() -> None:
    """Clear the intent match cache (called by admin endpoint)."""
    _intent_match_cache.clear()


def intent_cache_size() -> int:
    """Return current size of the intent match cache."""
    return len(_intent_match_cache)
