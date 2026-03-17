from __future__ import annotations

from google.cloud import firestore


PROJECT_ID = "agentic-ai-assistants-490311"


def upsert_many(client: firestore.Client, collection: str, docs: list[dict], id_field: str) -> None:
    for doc in docs:
        client.collection(collection).document(doc[id_field]).set(doc)


def main() -> None:
    db = firestore.Client(project=PROJECT_ID)

    users = [
        {
            "user_id": "u1001",
            "name": "John",
            "email": "john@example.com",
            "address": "Bengaluru",
        },
        {
            "user_id": "u1002",
            "name": "Priya",
            "email": "priya@example.com",
            "address": "Mumbai",
        },
        {
            "user_id": "u1003",
            "name": "Arjun",
            "email": "arjun@example.com",
            "address": "Hyderabad",
        },
        {
            "user_id": "u1004",
            "name": "Neha",
            "email": "neha@example.com",
            "address": "Delhi",
        },
    ]

    coupons = [
        {
            "code": "SAVE20",
            "description": "Flat 20% off",
            "status": "Active",
            "expiry": "2026-04-30",
        },
        {
            "code": "FESTIVE10",
            "description": "10% off up to 500",
            "status": "Active",
            "expiry": "2026-04-10",
        },
        {
            "code": "NEWUSER15",
            "description": "15% off for first order",
            "status": "Active",
            "expiry": "2026-05-15",
        },
        {
            "code": "FREESHIP",
            "description": "Free shipping above 999",
            "status": "Active",
            "expiry": "2026-06-01",
        },
    ]

    orders = [
        {
            "order_id": "12345",
            "user_id": "u1001",
            "status": "Shipped",
            "delivery_date": "2026-03-18",
            "address": "Bengaluru",
            "items": [{"item_id": "i1", "name": "Keyboard", "qty": 1}],
        },
        {
            "order_id": "10234",
            "user_id": "u1001",
            "status": "Processing",
            "delivery_date": "2026-03-20",
            "address": "Bengaluru",
            "items": [{"item_id": "i2", "name": "Mouse", "qty": 2}],
        },
        {
            "order_id": "22331",
            "user_id": "u1002",
            "status": "Delivered",
            "delivery_date": "2026-03-10",
            "address": "Mumbai",
            "items": [{"item_id": "i3", "name": "Laptop Stand", "qty": 1}],
        },
        {
            "order_id": "22332",
            "user_id": "u1003",
            "status": "Out for Delivery",
            "delivery_date": "2026-03-17",
            "address": "Hyderabad",
            "items": [{"item_id": "i4", "name": "USB Hub", "qty": 1}],
        },
    ]

    doctors = [
        {
            "doctor_id": "d100",
            "name": "Dr. Sharma",
            "specialty": "General Medicine",
            "slots": ["10:00", "11:30", "16:00"],
        },
        {
            "doctor_id": "d101",
            "name": "Dr. Rao",
            "specialty": "Cardiology",
            "slots": ["09:30", "14:00"],
        },
        {
            "doctor_id": "d102",
            "name": "Dr. Iyer",
            "specialty": "Dermatology",
            "slots": ["10:30", "12:00", "17:00"],
        },
        {
            "doctor_id": "d103",
            "name": "Dr. Khan",
            "specialty": "Orthopedics",
            "slots": ["09:00", "13:00", "15:30"],
        },
    ]

    flights = [
        {"flight_id": "F101", "from": "Delhi", "to": "Bangalore", "price": 5200},
        {"flight_id": "F203", "from": "Delhi", "to": "Bangalore", "price": 6100},
        {"flight_id": "F305", "from": "Mumbai", "to": "Goa", "price": 3400},
        {"flight_id": "F412", "from": "Bangalore", "to": "Kolkata", "price": 5800},
        {"flight_id": "F509", "from": "Hyderabad", "to": "Delhi", "price": 4900},
    ]

    travel_bookings = [
        {
            "booking_id": "t0001",
            "user_id": "u1001",
            "status": "Confirmed",
            "request": "Book hotel in Goa for 3 nights",
        },
        {
            "booking_id": "t0002",
            "user_id": "u1002",
            "status": "Cancelled",
            "request": "Book flight from Mumbai to Goa",
        },
    ]

    appointments = [
        {
            "appointment_id": "a0001",
            "user_id": "u1001",
            "status": "Booked",
            "request": "Consultation with Dr. Sharma tomorrow",
        },
        {
            "appointment_id": "a0002",
            "user_id": "u1002",
            "status": "Rescheduled",
            "request": "Follow-up with Dr. Rao next Monday",
        },
    ]

    upsert_many(db, "users", users, "user_id")
    upsert_many(db, "coupons", coupons, "code")
    upsert_many(db, "orders", orders, "order_id")
    upsert_many(db, "doctors", doctors, "doctor_id")
    upsert_many(db, "flights", flights, "flight_id")
    upsert_many(db, "travel_bookings", travel_bookings, "booking_id")
    upsert_many(db, "appointments", appointments, "appointment_id")

    print("Seed complete: users, coupons, orders, doctors, flights, travel_bookings, appointments")


if __name__ == "__main__":
    main()
