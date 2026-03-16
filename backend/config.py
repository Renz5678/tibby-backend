"""
config.py — Tibby Chatbot Configuration
All constants and environment-driven settings in one place.
"""

import os

# ==============================
# File Paths
# ==============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INTENTS_FILE = os.path.join(BASE_DIR, "intents.json")

# ==============================
# Rate Limiting
# ==============================
RATE_LIMIT_REQUESTS = 10   # max requests per window per user
RATE_LIMIT_WINDOW   = 60   # window size in seconds

# ==============================
# Response Cache
# ==============================
CACHE_TTL      = 1800  # 30 minutes
CACHE_MAX_SIZE = 200

# ==============================
# Input Validation
# ==============================
MAX_INPUT_LENGTH = 500
MIN_INPUT_LENGTH = 1

# ==============================
# Personality
# ==============================
PERSONALITY_EMOJIS = ["🐾", "😊", "✨", "💙", "🎓"]
CLOSING_PHRASES = [
    "Let me know if you have more questions!",
    "I'm here if you need more help!",
    "Feel free to ask anything else!",
    "Always happy to help, Gentinian!",
]

# ==============================
# Intent Matching
# ==============================
CONFIDENCE_THRESHOLD   = 0.70   # min confidence to accept a match
FUZZY_MATCH_CUTOFF     = 0.60   # lower bound for fuzzy score
MAX_PATTERNS_TO_CHECK  = 1000   # cap for performance

# ==============================
# CORS
# ==============================
_base_origins = [
    "http://localhost:5173",              # Vite dev server
    "http://localhost:3000",              # Alternative dev port
    "https://tibby-chatbot.vercel.app",  # Production frontend
    "https://tibby-ai.vercel.app",       # Production frontend (alt)
]
_custom_origin = os.getenv("FRONTEND_URL", "").strip()
if _custom_origin:
    _base_origins.append(_custom_origin)

ALLOWED_ORIGINS = _base_origins
