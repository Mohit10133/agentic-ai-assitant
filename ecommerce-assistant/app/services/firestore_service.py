from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any, Dict, List

from google.cloud import firestore


class DataStore:
    """Firestore-backed store with in-memory fallback for local dev."""

    def __init__(self) -> None:
        self.client = None
        self.use_firestore = False

        project_id = os.getenv("PROJECT_ID")
        try:
            self.client = firestore.Client(project=project_id)
            self.use_firestore = True
        except Exception:
            self.use_firestore = False

        # Local fallback data used when Firestore auth/client is unavailable.
        self.users: Dict[str, Dict[str, Any]] = {
            "u1001": {
                "user_id": "u1001",
                "name": "John",
                "email": "john@example.com",
                "address": "Bengaluru",
            }
        }
        self.orders: Dict[str, Dict[str, Any]] = {
            "12345": {
                "order_id": "12345",
                "user_id": "u1001",
                "status": "Shipped",
                "delivery_date": "2026-03-18",
                "address": "Bengaluru",
                "items": [{"item_id": "i1", "name": "Keyboard", "qty": 1}],
            },
            "10234": {
                "order_id": "10234",
                "user_id": "u1001",
                "status": "Processing",
                "delivery_date": "2026-03-20",
                "address": "Bengaluru",
                "items": [{"item_id": "i2", "name": "Mouse", "qty": 2}],
            },
        }
        self.coupons: Dict[str, Dict[str, Any]] = {
            "SAVE20": {
                "code": "SAVE20",
                "description": "Flat 20% off",
                "status": "Active",
                "expiry": "2026-04-30",
            },
            "FESTIVE10": {
                "code": "FESTIVE10",
                "description": "10% off up to 500",
                "status": "Active",
                "expiry": "2026-04-10",
            },
        }
        self.travel_bookings: Dict[str, Dict[str, Any]] = {}
        self.appointments: Dict[str, Dict[str, Any]] = {}
        self.chat_messages: List[Dict[str, Any]] = []

    def _doc(self, collection: str, doc_id: str):
        return self.client.collection(collection).document(doc_id)

    def _collection(self, collection: str):
        return self.client.collection(collection)

    def list_coupons(self) -> List[Dict[str, Any]]:
        if self.use_firestore:
            return [d.to_dict() for d in self._collection("coupons").stream()]
        return list(self.coupons.values())

    def get_coupon(self, code: str) -> Dict[str, Any] | None:
        if self.use_firestore:
            doc = self._doc("coupons", code).get()
            return doc.to_dict() if doc.exists else None
        return self.coupons.get(code)

    def get_order(self, order_id: str) -> Dict[str, Any] | None:
        if self.use_firestore:
            doc = self._doc("orders", order_id).get()
            return doc.to_dict() if doc.exists else None
        return self.orders.get(order_id)

    def update_order(self, order_id: str, payload: Dict[str, Any]) -> None:
        if self.use_firestore:
            self._doc("orders", order_id).set(payload)
            return
        self.orders[order_id] = payload

    def get_user(self, user_id: str) -> Dict[str, Any] | None:
        if self.use_firestore:
            doc = self._doc("users", user_id).get()
            return doc.to_dict() if doc.exists else None
        return self.users.get(user_id)

    def create_user(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        if self.use_firestore:
            self._doc("users", payload["user_id"]).set(payload)
            return payload
        self.users[payload["user_id"]] = payload
        return payload

    def next_user_id(self) -> str:
        if self.use_firestore:
            count = sum(1 for _ in self._collection("users").stream())
            return f"u{1000 + count + 1}"
        return f"u{1000 + len(self.users) + 1}"

    def list_user_orders(self, user_id: str) -> List[Dict[str, Any]]:
        if self.use_firestore:
            query = self._collection("orders").where("user_id", "==", user_id)
            return [d.to_dict() for d in query.stream()]
        return [o for o in self.orders.values() if o["user_id"] == user_id]

    def next_travel_booking_id(self) -> str:
        if self.use_firestore:
            count = sum(1 for _ in self._collection("travel_bookings").stream())
            return f"t{count + 1:04d}"
        return f"t{len(self.travel_bookings) + 1:04d}"

    def create_travel_booking(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        if self.use_firestore:
            self._doc("travel_bookings", payload["booking_id"]).set(payload)
            return payload
        self.travel_bookings[payload["booking_id"]] = payload
        return payload

    def list_travel_bookings(self, user_id: str) -> List[Dict[str, Any]]:
        if self.use_firestore:
            query = self._collection("travel_bookings").where("user_id", "==", user_id)
            return [d.to_dict() for d in query.stream()]
        return [b for b in self.travel_bookings.values() if b["user_id"] == user_id]

    def get_any_travel_booking(self) -> Dict[str, Any] | None:
        if self.use_firestore:
            docs = list(self._collection("travel_bookings").limit(1).stream())
            return docs[0].to_dict() if docs else None
        return next(iter(self.travel_bookings.values()), None)

    def update_travel_booking(self, booking_id: str, payload: Dict[str, Any]) -> None:
        if self.use_firestore:
            self._doc("travel_bookings", booking_id).set(payload)
            return
        self.travel_bookings[booking_id] = payload

    def next_appointment_id(self) -> str:
        if self.use_firestore:
            count = sum(1 for _ in self._collection("appointments").stream())
            return f"a{count + 1:04d}"
        return f"a{len(self.appointments) + 1:04d}"

    def create_appointment(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        if self.use_firestore:
            self._doc("appointments", payload["appointment_id"]).set(payload)
            return payload
        self.appointments[payload["appointment_id"]] = payload
        return payload

    def get_any_appointment(self) -> Dict[str, Any] | None:
        if self.use_firestore:
            docs = list(self._collection("appointments").limit(1).stream())
            return docs[0].to_dict() if docs else None
        return next(iter(self.appointments.values()), None)

    def update_appointment(self, appointment_id: str, payload: Dict[str, Any]) -> None:
        if self.use_firestore:
            self._doc("appointments", appointment_id).set(payload)
            return
        self.appointments[appointment_id] = payload

    def save_chat_message(self, user_id: str, role: str, text: str, detected_domain: str = "") -> Dict[str, Any]:
        payload = {
            "user_id": user_id,
            "role": role,
            "text": text,
            "detected_domain": detected_domain,
            "created_ts": datetime.now(timezone.utc).timestamp(),
        }
        if self.use_firestore:
            self._collection("chat_messages").add(payload)
            return payload
        self.chat_messages.append(payload)
        return payload

    def list_chat_messages(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        if self.use_firestore:
            query = self._collection("chat_messages").where("user_id", "==", user_id)
            rows = [d.to_dict() for d in query.stream()]
        else:
            rows = [m for m in self.chat_messages if m.get("user_id") == user_id]

        rows.sort(key=lambda r: float(r.get("created_ts", 0)))
        if limit > 0:
            rows = rows[-limit:]
        return rows

    def delete_chat_messages(self, user_id: str) -> int:
        """Delete all chat messages for a user. Returns count of deleted messages."""
        if self.use_firestore:
            query = self._collection("chat_messages").where("user_id", "==", user_id)
            docs = query.stream()
            count = 0
            for doc in docs:
                doc.reference.delete()
                count += 1
            return count
        else:
            original_count = len(self.chat_messages)
            self.chat_messages = [m for m in self.chat_messages if m.get("user_id") != user_id]
            return original_count - len(self.chat_messages)


store = DataStore()
