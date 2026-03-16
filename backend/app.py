"""
app.py — Tibby Chatbot Entry Point
Creates and configures the Flask application.
Run locally  : python app.py
Run on Render: gunicorn --chdir backend app:app
"""

import os

from flask import Flask
from flask_cors import CORS

from config import ALLOWED_ORIGINS
from routes import bp


def create_app() -> Flask:
    """Application factory — creates and returns a configured Flask app."""
    application = Flask(__name__)

    # CORS
    CORS(application, resources={"/*": {"origins": ALLOWED_ORIGINS}})

    # Register all routes via Blueprint
    application.register_blueprint(bp)

    return application


# Module-level app instance (needed by gunicorn: app:app)
app = create_app()


if __name__ == "__main__":
    from intents import intents_data
    from config import RATE_LIMIT_REQUESTS, CACHE_MAX_SIZE, CACHE_TTL

    print("\n" + "=" * 50)
    print("🚀 Starting Tibby Chatbot Server (v2.0 — Modular)")
    print("=" * 50)
    print(f"📍 API:           http://localhost:5000/")
    print(f"💬 Chat:          POST http://localhost:5000/chat")
    print(f"❤️  Health check:  http://localhost:5000/health")
    print(f"📚 Intents loaded: {len(intents_data.get('intents', []))}")
    print(f"🔒 Rate limit:    {RATE_LIMIT_REQUESTS} req/min per user")
    print(f"💾 Cache:         {CACHE_MAX_SIZE} items, {CACHE_TTL}s TTL")
    print("=" * 50 + "\n")

    app.run(
        debug=os.getenv("FLASK_DEBUG", "false").lower() == "true",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 5000)),
    )