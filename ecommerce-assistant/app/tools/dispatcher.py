from __future__ import annotations

from typing import Any, Dict

from app.services.vertex_service import router
from app.tools.ecommerce import handle_ecommerce
from app.tools.healthcare import handle_healthcare
from app.tools.travel import handle_travel


VALID_DOMAINS = ("ecommerce", "travel", "healthcare")


DOMAIN_INTENTS = {
    "ecommerce": {
        "coupon.list",
        "coupon.details",
        "order.status",
        "order.details",
        "order.cancel",
        "user.register",
        "user.details",
        "knowledge.qa",
    },
    "travel": {
        "travel.search_flights",
        "travel.book",
        "travel.cancel",
        "travel.itinerary",
        "knowledge.qa",
    },
    "healthcare": {
        "health.doctor_availability",
        "health.book_appointment",
        "health.cancel_appointment",
        "health.reschedule_appointment",
        "health.records",
        "knowledge.qa",
    },
}


def _canonical_message(domain: str, intent: str, entities: Dict[str, Any]) -> str:
    order_id = str(entities.get("order_id", "")).strip()
    coupon_code = str(entities.get("coupon_code", "")).strip()
    email = str(entities.get("email", "")).strip()
    from_city = str(entities.get("from_city", "Delhi")).strip() or "Delhi"
    to_city = str(entities.get("to_city", "Bangalore")).strip() or "Bangalore"

    if domain == "ecommerce":
        mapping = {
            "coupon.list": "Show available coupons",
            "coupon.details": f"Check coupon {coupon_code or 'SAVE20'}",
            "order.status": f"What is the status of my order {order_id or '12345'}?",
            "order.details": f"Show details of order {order_id or '12345'}",
            "order.cancel": f"Cancel order {order_id or '10234'}",
            "user.register": f"Register a new user with email {email or 'test@example.com'}",
            "user.details": "Show my profile details",
            "knowledge.qa": "How can I apply a coupon?",
        }
        return mapping.get(intent, "")

    if domain == "travel":
        mapping = {
            "travel.search_flights": f"Search flights from {from_city} to {to_city}",
            "travel.book": "Book hotel in Goa for 3 nights",
            "travel.cancel": "Cancel my flight booking",
            "travel.itinerary": "Show my itinerary",
            "knowledge.qa": "What is the baggage limit for domestic flights?",
        }
        return mapping.get(intent, "")

    if domain == "healthcare":
        mapping = {
            "health.doctor_availability": "Check doctor availability",
            "health.book_appointment": "Book an appointment with Dr. Sharma tomorrow",
            "health.cancel_appointment": "Cancel my appointment for Monday",
            "health.reschedule_appointment": "Reschedule my appointment",
            "health.records": "Show my medical records",
            "knowledge.qa": "What are hospital visiting hours?",
        }
        return mapping.get(intent, "")

    return ""


def _route_fixed_domain(domain: str, message: str, user_id: str) -> Dict[str, Any]:
    routed_message = message
    prediction = router.classify(domain, message)
    if prediction.get("enabled") and prediction.get("parsed"):
        intent = str(prediction.get("intent", "")).strip()
        entities = prediction.get("entities", {}) or {}
        candidate = _canonical_message(domain, intent, entities)
        if candidate:
            routed_message = candidate

    if domain == "ecommerce":
        return handle_ecommerce(message=routed_message, user_id=user_id)
    if domain == "travel":
        return handle_travel(message=routed_message, user_id=user_id)
    return handle_healthcare(message=routed_message, user_id=user_id)


def _detect_domain(message: str) -> str:
    # Try LLM-based detection first when Vertex router is enabled.
    if getattr(router, "enabled", False):
        ranked = []
        for candidate in VALID_DOMAINS:
            prediction = router.classify(candidate, message)
            if prediction.get("enabled") and prediction.get("parsed"):
                intent = str(prediction.get("intent", "")).strip()
                if intent in DOMAIN_INTENTS.get(candidate, set()):
                    score = 1 if intent == "knowledge.qa" else 2
                    ranked.append((score, candidate))
        if ranked:
            ranked.sort(reverse=True)
            return ranked[0][1]

    # Fallback to keyword scoring when Vertex is disabled or returns no parse.
    m = message.lower()
    scores = {"ecommerce": 0, "travel": 0, "healthcare": 0}

    ecommerce_hints = [
        "order", "coupon", "cart", "delivery", "refund", "return", "address", "quantity", "profile", "account",
    ]
    travel_hints = [
        "flight", "hotel", "trip", "itinerary", "visa", "baggage", "airport", "boarding", "ticket", "booking",
    ]
    healthcare_hints = [
        "doctor", "hospital", "appointment", "medical", "records", "pharmacy", "lab", "clinic", "patient", "visiting",
    ]

    for token in ecommerce_hints:
        if token in m:
            scores["ecommerce"] += 1
    for token in travel_hints:
        if token in m:
            scores["travel"] += 1
    for token in healthcare_hints:
        if token in m:
            scores["healthcare"] += 1

    ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    best_domain, best_score = ranked[0]
    return best_domain if best_score > 0 else "ecommerce"


def _attach_detected_domain(result: Dict[str, Any], domain: str) -> Dict[str, Any]:
    payload = result.get("data")
    if isinstance(payload, dict):
        payload["detected_domain"] = domain
    else:
        result["data"] = {"detected_domain": domain}
    return result


def dispatch(domain: str, message: str, user_id: str) -> Dict[str, Any]:
    d = domain.strip().lower()

    if d in VALID_DOMAINS:
        return _attach_detected_domain(_route_fixed_domain(domain=d, message=message, user_id=user_id), d)

    if d in ("auto", "", "chat", "general"):
        guessed = _detect_domain(message)
        domain_order = [guessed] + [candidate for candidate in VALID_DOMAINS if candidate != guessed]

        fallback_result = None
        for candidate in domain_order:
            result = _route_fixed_domain(domain=candidate, message=message, user_id=user_id)
            if fallback_result is None:
                fallback_result = result
            if result.get("intent") != "unknown":
                return _attach_detected_domain(result, candidate)

        return _attach_detected_domain(fallback_result or {
            "success": False,
            "message": "I could not understand your request yet",
            "intent": "unknown",
            "data": {},
        }, guessed)

    return {
        "success": False,
        "message": "Invalid domain. Use auto, ecommerce, travel, or healthcare.",
        "intent": "invalid_domain",
        "data": {},
    }
