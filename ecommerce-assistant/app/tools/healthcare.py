from __future__ import annotations

from typing import Any, Dict

from app.services.firestore_service import store
from app.services.knowledge_service import answer_knowledge_query


def handle_healthcare(message: str, user_id: str) -> Dict[str, Any]:
    m = message.lower()

    if "availability" in m or "available" in m and "dr" in m:
        return {
            "success": True,
            "message": "Doctor availability fetched",
            "intent": "health.doctor_availability",
            "data": {
                "doctors": [
                    {"name": "Dr. Sharma", "slots": ["10:00", "11:30", "16:00"]},
                    {"name": "Dr. Rao", "slots": ["09:30", "14:00"]},
                ]
            },
        }

    if ("book" in m and "appointment" in m) or "consultation" in m:
        appt_id = store.next_appointment_id()
        payload = {
            "appointment_id": appt_id,
            "user_id": user_id,
            "status": "Booked",
            "request": message,
        }
        store.create_appointment(payload)
        return {
            "success": True,
            "message": f"Appointment booked: {appt_id}",
            "intent": "health.book_appointment",
            "data": payload,
        }

    if "cancel" in m and "appointment" in m:
        first = store.get_any_appointment()
        if not first:
            return {
                "success": False,
                "message": "No appointment found to cancel",
                "intent": "health.cancel_appointment",
                "data": {},
            }
        first["status"] = "Cancelled"
        store.update_appointment(first["appointment_id"], first)
        return {
            "success": True,
            "message": f"Appointment {first['appointment_id']} cancelled",
            "intent": "health.cancel_appointment",
            "data": first,
        }

    if "reschedule" in m:
        first = store.get_any_appointment()
        if not first:
            return {
                "success": False,
                "message": "No appointment found to reschedule",
                "intent": "health.reschedule_appointment",
                "data": {},
            }
        first["status"] = "Rescheduled"
        store.update_appointment(first["appointment_id"], first)
        return {
            "success": True,
            "message": f"Appointment {first['appointment_id']} rescheduled",
            "intent": "health.reschedule_appointment",
            "data": first,
        }

    if "medical records" in m or "my records" in m:
        return {
            "success": True,
            "message": "Medical records fetched",
            "intent": "health.records",
            "data": {
                "records": [
                    {"date": "2026-01-12", "summary": "General checkup"},
                    {"date": "2026-02-25", "summary": "Blood test"},
                ]
            },
        }

    if "visiting hours" in m or "documents" in m or "prepare" in m:
        return answer_knowledge_query(domain="healthcare", query=message)

    return {
        "success": False,
        "message": "I could not map this healthcare request yet",
        "intent": "unknown",
        "data": {},
    }
