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
    """
    API root — returns basic status information.
    ---
    tags:
      - General
    summary: API status check
    description: Returns the current API version, status, and number of intents loaded.
    produces:
      - application/json
    responses:
      200:
        description: API is running normally
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Tibby API is running"
            version:
              type: string
              example: "2.0.0 (Intent-Only)"
            status:
              type: string
              example: "healthy"
            intents_loaded:
              type: integer
              example: 42
    """
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
    Send a message to Tibby and receive a chatbot response.
    ---
    tags:
      - Chat
    summary: Chat with Tibby
    description: >
      Accepts a user message and returns a matched intent reply.
      Responses are cached for 30 minutes. The endpoint is rate-limited
      to 10 requests per minute per IP address.
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        description: The user's chat message
        schema:
          type: object
          required:
            - message
          properties:
            message:
              type: string
              minLength: 1
              maxLength: 500
              example: "What are the enrollment requirements?"
    responses:
      200:
        description: Successful chatbot reply
        schema:
          type: object
          properties:
            reply:
              type: string
              example: "🐾 Enrollment at GTDLNHS requires... Let me know if you have more questions!"
            confidence:
              type: number
              format: float
              example: 0.92
            cached:
              type: boolean
              example: false
      400:
        description: Bad request — missing or invalid message
        schema:
          type: object
          properties:
            reply:
              type: string
              example: "⚠️ Please provide a message in JSON format with a 'message' key."
            confidence:
              type: number
              example: 0.0
      429:
        description: Rate limit exceeded
        schema:
          type: object
          properties:
            reply:
              type: string
              example: "⚠️ Too many requests. Please wait a moment before trying again."
            confidence:
              type: number
              example: 0.0
      500:
        description: Internal server error
        schema:
          type: object
          properties:
            reply:
              type: string
              example: "⚠️ Oops! Something went wrong on my end. Please try again!"
            confidence:
              type: number
              example: 0.0
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
    """
    Health check with basic performance metrics.
    ---
    tags:
      - Health & Monitoring
    summary: Server health check
    description: Returns server health status along with cache sizes and total pattern count.
    produces:
      - application/json
    responses:
      200:
        description: Server is healthy
        schema:
          type: object
          properties:
            status:
              type: string
              example: "healthy"
            intents_loaded:
              type: integer
              example: 42
            response_cache_size:
              type: integer
              example: 17
            intent_cache_size:
              type: integer
              example: 5
            total_patterns:
              type: integer
              example: 320
            timestamp:
              type: string
              format: date-time
              example: "2025-01-01T12:00:00.000000"
    """
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
    """
    Clear all server-side caches (admin operation).
    ---
    tags:
      - Admin
    summary: Clear all caches
    description: >
      Flushes both the response cache and the intent matching cache.
      Use this after updating intents.json or to free up memory.
    produces:
      - application/json
    responses:
      200:
        description: All caches cleared successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: "All caches cleared successfully"
            response_cache:
              type: string
              example: "cleared"
            intent_cache:
              type: string
              example: "cleared"
            timestamp:
              type: string
              format: date-time
              example: "2025-01-01T12:00:00.000000"
    """
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
    """
    Chatbot statistics overview.
    ---
    tags:
      - Health & Monitoring
    summary: Chatbot performance statistics
    description: >
      Returns counts of intents, patterns, and current cache usage,
      along with configured thresholds and rate-limit settings.
    produces:
      - application/json
    responses:
      200:
        description: Statistics retrieved successfully
        schema:
          type: object
          properties:
            intents:
              type: integer
              example: 42
            total_patterns:
              type: integer
              example: 320
            avg_patterns_per_intent:
              type: number
              format: float
              example: 7.62
            response_cache_size:
              type: integer
              example: 17
            intent_cache_size:
              type: integer
              example: 5
            cache_max_size:
              type: integer
              example: 200
            cache_ttl_seconds:
              type: integer
              example: 1800
            confidence_threshold:
              type: number
              format: float
              example: 0.7
            rate_limit:
              type: string
              example: "10 req/min"
    """
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
