"""
routes.py — Tibby Chatbot Route Handlers
All Flask endpoints registered on a Blueprint.
"""

from datetime import datetime

from flask import Blueprint, jsonify, request

from cache import response_cache
from intents import (
    intent_cache_size,
    intents_data,
    clear_intent_cache,
    match_intent,
)
from rate_limiter import rate_limiter
from utils import validate_input

bp = Blueprint("tibby", __name__)


# ==============================
# GET /
# ==============================
@bp.route("/", methods=["GET"])
def home():
    """API status endpoint."""
    return jsonify({
        "message": "Tibby API is running",
        "version": "2.0.0 (Intent-Only)",
        "status": "healthy",
        "intents_loaded": len(intents_data.get("intents", [])),
    }), 200


# ==============================
# POST /chat
# ==============================
@bp.route("/chat", methods=["POST"])
def chat():
    """
    Handle chat requests.

    Expected JSON body : {"message": "your question here"}
    Response JSON      : {"reply": "...", "confidence": 0.95, "cached": false}
    """
    try:
        user_ip = request.remote_addr or "unknown"

        # Rate limit check
        if not rate_limiter.is_allowed(user_ip):
            return jsonify({
                "reply": "⚠️ Too many requests. Please wait a moment before trying again.",
                "confidence": 0.0,
            }), 429

        # Parse & validate JSON body
        data = request.get_json()
        if not data or "message" not in data:
            return jsonify({
                "reply": "⚠️ Please provide a message in JSON format with a 'message' key.",
                "confidence": 0.0,
            }), 400

        user_input = data.get("message", "").strip()

        is_valid, error_msg = validate_input(user_input)
        if not is_valid:
            return jsonify({"reply": error_msg, "confidence": 0.0}), 400

        # Response cache hit
        cache_key = user_input.lower()
        cached = response_cache.get(cache_key)
        if cached:
            return jsonify({"reply": cached, "confidence": 1.0, "cached": True}), 200

        # Intent matching
        intent_reply, confidence = match_intent(user_input)
        if intent_reply and confidence >= 0.70:
            response_cache.set(cache_key, intent_reply)
            return jsonify({
                "reply": intent_reply,
                "confidence": confidence,
                "cached": False,
            }), 200

        # Fallback reply
        fallback = (
            "🐾 I'm sorry, I don't have information about that yet. "
            "I can help with questions about GTDLNHS like:\n"
            "• Enrollment and admissions\n"
            "• School facilities and location\n"
            "• Schedules and programs\n"
            "• Clubs and organizations\n"
            "• School policies\n\n"
            "What would you like to know about GTDLNHS?"
        )
        return jsonify({"reply": fallback, "confidence": 0.0}), 200

    except Exception as e:
        print(f"❌ Error in /chat endpoint: {e}")
        return jsonify({
            "reply": "⚠️ Oops! Something went wrong on my end. Please try again!",
            "confidence": 0.0,
        }), 500


# ==============================
# GET /health
# ==============================
@bp.route("/health", methods=["GET"])
def health():
    """Health check with basic performance metrics."""
    return jsonify({
        "status": "healthy",
        "intents_loaded": len(intents_data.get("intents", [])),
        "response_cache_size": len(response_cache.cache),
        "intent_cache_size": intent_cache_size(),
        "total_patterns": sum(
            len(i.get("patterns", [])) for i in intents_data.get("intents", [])
        ),
        "timestamp": datetime.now().isoformat(),
    }), 200


# ==============================
# POST /cache/clear
# ==============================
@bp.route("/cache/clear", methods=["POST"])
def clear_cache():
    """Admin endpoint — clears both response and intent caches."""
    response_cache.clear()
    clear_intent_cache()
    return jsonify({
        "message": "All caches cleared successfully",
        "response_cache": "cleared",
        "intent_cache": "cleared",
        "timestamp": datetime.now().isoformat(),
    }), 200


# ==============================
# GET /stats
# ==============================
@bp.route("/stats", methods=["GET"])
def stats():
    """Chatbot statistics overview."""
    from config import (
        CACHE_MAX_SIZE, CACHE_TTL, CONFIDENCE_THRESHOLD, RATE_LIMIT_REQUESTS
    )

    intent_list = intents_data.get("intents", [])
    total_patterns = sum(len(i.get("patterns", [])) for i in intent_list)
    avg_patterns = total_patterns / len(intent_list) if intent_list else 0

    return jsonify({
        "intents": len(intent_list),
        "total_patterns": total_patterns,
        "avg_patterns_per_intent": round(avg_patterns, 2),
        "response_cache_size": len(response_cache.cache),
        "intent_cache_size": intent_cache_size(),
        "cache_max_size": CACHE_MAX_SIZE,
        "cache_ttl_seconds": CACHE_TTL,
        "confidence_threshold": CONFIDENCE_THRESHOLD,
        "rate_limit": f"{RATE_LIMIT_REQUESTS} req/min",
    }), 200
