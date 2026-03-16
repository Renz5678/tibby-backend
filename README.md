# Tibby Chatbot — Backend

A Flask-based chatbot API for **General Tiburcio de Leon National High School (GTDLNHS)**.  
Uses intent matching (exact + fuzzy) to answer school-related queries, with LRU response caching and per-IP rate limiting.

---

## Project Structure

```
tibby backen/
├── backend/
│   ├── app.py           # Flask app factory & entry point
│   ├── config.py        # All constants & env-driven settings
│   ├── cache.py         # SimpleCache (LRU + TTL)
│   ├── rate_limiter.py  # Sliding-window rate limiter
│   ├── intents.py       # Intent loading & fuzzy matching
│   ├── utils.py         # format_response, validate_input
│   ├── routes.py        # Flask Blueprint — all API routes
│   ├── intents.json     # Intent data
│   └── intents_expanded.json
├── requirements.txt
├── render.yaml          # Render deploy config
├── .env.example         # Env var reference
└── README.md
```

---

## Local Development

### 1. Create & activate virtual environment

```bash
# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

```bash
# Copy the example and fill in your values
copy .env.example .env       # Windows
cp .env.example .env         # macOS/Linux
```

### 4. Run the server

```bash
python backend/app.py
```

Server starts at **http://localhost:5000**

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Status check |
| POST | `/chat` | Send a message, get a reply |
| GET | `/health` | Health + cache metrics |
| GET | `/stats` | Intent & cache statistics |
| POST | `/cache/clear` | Clear all caches (admin) |

### Chat request example

```bash
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "how do I enroll?"}'
```

---

## Deploy to Render

1. Push this repo to GitHub (or GitLab).
2. Go to [https://render.com](https://render.com) → **New Web Service**.
3. Connect your repository — Render will auto-detect `render.yaml`.
4. Set the `FRONTEND_URL` environment variable in the Render dashboard to your frontend's deployed URL.
5. Click **Deploy** — Render will install dependencies and start gunicorn automatically.

> **Note:** The free Render tier spins down after inactivity. The first request after idle may be slow (~30 s cold start).
