from __future__ import annotations

from typing import Any, Dict

from app.services.firestore_service import store
from app.services.knowledge_service import answer_knowledge_query


def handle_travel(message: str, user_id: str) -> Dict[str, Any]:
    m = message.lower()

    if "search flight" in m or "flights from" in m or ("need a flight" in m and "from" in m and "to" in m):
        return {
            "success": True,
            "message": "Sample flights found",
            "intent": "travel.search_flights",
            "data": {
                "results": [
                    {"flight_id": "F101", "from": "Delhi", "to": "Bangalore", "price": 5200},
                    {"flight_id": "F203", "from": "Delhi", "to": "Bangalore", "price": 6100},
                ]
            },
        }

    if "book hotel" in m or "book flight" in m or "book ticket" in m:
        booking_id = store.next_travel_booking_id()
        payload = {
            "booking_id": booking_id,
            "user_id": user_id,
            "status": "Confirmed",
            "request": message,
        }
        store.create_travel_booking(payload)
        return {
            "success": True,
            "message": f"Booking confirmed: {booking_id}",
            "intent": "travel.book",
            "data": payload,
        }

    if "cancel" in m and "booking" in m:
        first = store.get_any_travel_booking()
        if not first:
            return {
                "success": False,
                "message": "No bookings found for cancellation",
                "intent": "travel.cancel",
                "data": {},
            }
        first["status"] = "Cancelled"
        store.update_travel_booking(first["booking_id"], first)
        return {
            "success": True,
            "message": f"Booking {first['booking_id']} cancelled",
            "intent": "travel.cancel",
            "data": first,
        }

    if "itinerary" in m:
        items = store.list_travel_bookings(user_id)
        return {
            "success": True,
            "message": "Itinerary fetched",
            "intent": "travel.itinerary",
            "data": {"bookings": items},
        }

    if "baggage" in m or "visa" in m or "insurance" in m:
        return answer_knowledge_query(domain="travel", query=message)

    return {
        "success": False,
        "message": "I could not map this travel request yet",
        "intent": "unknown",
        "data": {},
    }
