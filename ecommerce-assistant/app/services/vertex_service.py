from __future__ import annotations

import json
import os
from importlib import import_module
from typing import Any, Dict


class VertexIntentRouter:
    def __init__(self) -> None:
        self.project_id = os.getenv("PROJECT_ID", "")
        self.region = os.getenv("REGION", "asia-south1")
        self.model_name = os.getenv("MODEL_NAME", "gemini-1.5-flash")
        self.enabled = os.getenv("USE_VERTEX_ROUTER", "false").lower() == "true"
        self._model = None

        if self.enabled and self.project_id:
            try:
                vertexai = import_module("vertexai")
                gen_models = import_module("vertexai.generative_models")
                GenerativeModel = getattr(gen_models, "GenerativeModel")
                vertexai.init(project=self.project_id, location=self.region)
                self._model = GenerativeModel(self.model_name)
            except Exception:
                self.enabled = False
                self._model = None

    def classify(self, domain: str, message: str) -> Dict[str, Any]:
        if not self.enabled or not self._model:
            return {"enabled": False}

        prompt = f"""
You are an intent classifier for a {domain} assistant.
Return strict JSON only with this schema:
{{
  "intent": "string",
  "entities": {{"order_id": "", "coupon_code": "", "email": "", "doctor_name": "", "from_city": "", "to_city": ""}}
}}

Allowed intents by domain:
- ecommerce: coupon.list, coupon.details, order.status, order.details, order.cancel, user.register, user.details, knowledge.qa
- travel: travel.search_flights, travel.book, travel.cancel, travel.itinerary, knowledge.qa
- healthcare: health.doctor_availability, health.book_appointment, health.cancel_appointment, health.reschedule_appointment, health.records, knowledge.qa

User message: {message}
""".strip()

        try:
            response = self._model.generate_content(prompt)
            text = (response.text or "").strip()
            start = text.find("{")
            end = text.rfind("}")
            if start == -1 or end == -1:
                return {"enabled": True, "parsed": False}
            payload = json.loads(text[start : end + 1])
            payload["enabled"] = True
            payload["parsed"] = True
            return payload
        except Exception:
            return {"enabled": True, "parsed": False}


router = VertexIntentRouter()
