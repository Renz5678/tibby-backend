"""
app.py — Tibby Chatbot Entry Point
Creates and configures the Flask application.
Run locally  : python app.py
Run on Render: gunicorn --chdir backend app:app
"""

import os

from flask import Flask
from flask_cors import CORS
from flasgger import Swagger

from config import ALLOWED_ORIGINS
from routes import bp


# ──────────────────────────────────────────────
# Swagger / OpenAPI base configuration
# ──────────────────────────────────────────────
SWAGGER_CONFIG = {
    "swagger": "2.0",
    "info": {
        "title": "Tibby Chatbot API",
        "description": (
            "REST API for Tibby — the AI-powered school assistant chatbot for "
            "Governor Teodoro D. Lerma National High School (GTDLNHS). "
            "Tibby answers student questions about enrollment, facilities, "
            "schedules, clubs, and school policies using intent-based matching."
        ),
        "version": "2.0.0",
        "contact": {
            "name": "Tibby Dev Team",
        },
        "license": {
            "name": "MIT",
        },
    },
    "basePath": "/",
    "tags": [
        {
            "name": "General",
            "description": "API root and status endpoints",
        },
        {
            "name": "Chat",
            "description": "Core chatbot interaction endpoint",
        },
        {
            "name": "Health & Monitoring",
            "description": "Health checks and performance statistics",
        },
        {
            "name": "Admin",
            "description": "Administrative operations (cache management)",
        },
    ],
    "consumes": ["application/json"],
    "produces": ["application/json"],
}

FLASGGER_CONFIG = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec",
            "route": "/apispec.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs",
}


def create_app() -> Flask:
    """Application factory — creates and returns a configured Flask app."""
    application = Flask(__name__)

    # CORS
    CORS(application, resources={"/*": {"origins": ALLOWED_ORIGINS}})

    # Swagger UI
    Swagger(application, template=SWAGGER_CONFIG, config=FLASGGER_CONFIG)

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
    print(f"📚 Swagger UI:    http://localhost:5000/apidocs")
    print(f"📚 Intents loaded: {len(intents_data.get('intents', []))}")
    print(f"🔒 Rate limit:    {RATE_LIMIT_REQUESTS} req/min per user")
    print(f"💾 Cache:         {CACHE_MAX_SIZE} items, {CACHE_TTL}s TTL")
    print("=" * 50 + "\n")

    app.run(
        debug=os.getenv("FLASK_DEBUG", "false").lower() == "true",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 5000)),
    )