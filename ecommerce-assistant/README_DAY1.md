# Day 1 Run Guide

## 1) Create and activate virtual environment

PowerShell:

python -m venv .venv
.\.venv\Scripts\Activate.ps1

## 2) Install dependencies

pip install -r requirements.txt

## 3) Run API locally

uvicorn app.main:app --reload --port 8000

## 4) Test endpoints

Health:

GET http://127.0.0.1:8000/health

Chat:

POST http://127.0.0.1:8000/chat
Content-Type: application/json

{
  "domain": "ecommerce",
  "user_id": "u1001",
  "message": "Show available coupons"
}

## 5) Example demo queries

- ecommerce: What is the status of my order 12345?
- travel: Search flights from Delhi to Bangalore
- healthcare: Book an appointment with Dr. Sharma tomorrow
