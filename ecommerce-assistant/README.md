# Agentic Multi-Domain Assistant

FastAPI-based assistant that handles Ecommerce, Travel, and Healthcare requests with domain routing, task handlers, and a built-in web chat UI.

## Features

- Multi-domain routing (auto domain detection)
- Vertex AI routing support (Gemini) via environment toggle
- Rule-based task handlers for ecommerce, travel, and healthcare
- Firestore-backed data store with in-memory fallback
- Chat history persistence per user
- Clear-chat API for resetting conversation history
- Built-in browser UI served from the API

## Project Structure

```text
app/
  main.py                  # FastAPI app + web UI + routes
  models/schemas.py        # Request/response schemas
  services/
    firestore_service.py   # Firestore + in-memory data store
    knowledge_service.py   # Domain knowledge response helper
    vertex_service.py      # Vertex/Gemini routing helper
  tools/
    dispatcher.py          # Domain dispatch logic
    ecommerce.py           # Ecommerce intents and actions
    travel.py              # Travel intents and actions
    healthcare.py          # Healthcare intents and actions
knowledge/                 # Domain knowledge markdown files
scripts/seed_firestore.py  # Optional Firestore seed script
```

## Requirements

- Python 3.11+
- pip
- Optional: GCP project + Firestore + Vertex AI access

## Environment Variables

Use `.env.example` as reference:

```env
PROJECT_ID=agentic-ai-assistants-490311
REGION=asia-south1
MODEL_NAME=gemini-1.5-flash
USE_VERTEX_ROUTER=true
```

Notes:
- `USE_VERTEX_ROUTER=true` enables Vertex-based routing.
- If Firestore/Vertex credentials are unavailable, some features fall back to in-memory logic.

## Local Setup

### 1) Create and activate virtual environment

PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2) Install dependencies

```powershell
pip install -r requirements.txt
```

### 3) Run the app

```powershell
uvicorn app.main:app --reload --port 8000
```

### 4) Open UI

- http://127.0.0.1:8000/
- or http://127.0.0.1:8000/ui

## API Endpoints

- `GET /` -> Web UI
- `GET /ui` -> Web UI
- `POST /ui` -> Legacy form-style UI post handler
- `GET /health` -> Health check
- `POST /chat` -> Main chat endpoint
- `GET /history/{user_id}` -> Chat history for user
- `DELETE /clear/{user_id}` -> Delete user chat history

## Example Chat Requests

### Coupon list

```json
{
  "domain": "auto",
  "user_id": "u1001",
  "message": "Show available coupons"
}
```

### Coupon details

```json
{
  "domain": "auto",
  "user_id": "u1001",
  "message": "Check coupon SAVE20"
}
```

### Order cancellation (safe behavior)

- Question-style text like `How do I cancel my order?` returns guidance.
- Explicit command text like `Cancel order 10234` performs cancellation.

### Address update

- `Change delivery address for order 10234 to 42 Main Street`
- If order ID is omitted, handler attempts latest user order.

## Optional: Seed Firestore Data

Run:

```powershell
python scripts/seed_firestore.py
```

This script inserts demo users, orders, coupons, doctors, flights, travel bookings, and appointments.

## Deploy to Cloud Run

From repo root:

```powershell
gcloud run deploy multi-domain-assistant --source . --region asia-south1 --platform managed --allow-unauthenticated --project agentic-ai-assistants-490311 --quiet
```

## Troubleshooting

- If responses look generic, verify routing env vars and deployment revision env settings.
- If Firestore reads fail, ensure service account permissions and project are correct.
- If UI actions do not reflect latest behavior, redeploy and hard-refresh browser.

## Current Stack

- FastAPI
- Uvicorn
- Pydantic v2
- Google Cloud Firestore
- Google Cloud Vertex AI
