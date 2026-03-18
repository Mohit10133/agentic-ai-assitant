from __future__ import annotations

from typing import Any, Dict

from app.services.firestore_service import store
from app.services.knowledge_service import answer_knowledge_query


def handle_ecommerce(message: str, user_id: str) -> Dict[str, Any]:
    m = message.lower()

    if (
        "available coupon" in m
        or "show coupon" in m
        or "coupons" in m
        or "discount code" in m
        or "discount codes" in m
        or "promo code" in m
    ):
        return {
            "success": True,
            "message": "Available coupons fetched",
            "intent": "coupon.list",
            "data": {"coupons": store.list_coupons()},
        }

    if "check coupon" in m or "details for coupon" in m:
        code = message.split()[-1].upper().strip("?.")
        coupon = store.get_coupon(code)
        if not coupon:
            return {
                "success": False,
                "message": f"Coupon {code} not found",
                "intent": "coupon.details",
                "data": {},
            }
        return {
            "success": True,
            "message": f"Coupon {code} details",
            "intent": "coupon.details",
            "data": coupon,
        }

    if "status of my order" in m or "status of order" in m:
        order_id = ''.join(ch for ch in message if ch.isdigit())
        order = store.get_order(order_id)
        if not order or order["user_id"] != user_id:
            return {
                "success": False,
                "message": f"Order {order_id} not found",
                "intent": "order.status",
                "data": {},
            }
        return {
            "success": True,
            "message": f"Order {order_id} status: {order['status']}",
            "intent": "order.status",
            "data": {"order_id": order_id, "status": order["status"]},
        }

    if "when will" in m and "order" in m or "delivery date" in m or "when is my order" in m or "delivered" in m and "order" in m:
        order_id = ''.join(ch for ch in message if ch.isdigit())
        order = store.get_order(order_id) if order_id else None
        if not order:
            # return first order for this user if no id given
            orders = store.list_user_orders(user_id)
            order = orders[0] if orders else None
        if not order:
            return {
                "success": False,
                "message": "No order found to check delivery date",
                "intent": "order.delivery",
                "data": {},
            }
        return {
            "success": True,
            "message": f"Order {order['order_id']} expected delivery: {order.get('delivery_date', 'Not available')}",
            "intent": "order.delivery",
            "data": {"order_id": order["order_id"], "delivery_date": order.get("delivery_date")},
        }

    if "details of order" in m or "show details of order" in m:
        order_id = ''.join(ch for ch in message if ch.isdigit())
        order = store.get_order(order_id)
        if not order or order["user_id"] != user_id:
            return {
                "success": False,
                "message": f"Order {order_id} not found",
                "intent": "order.details",
                "data": {},
            }
        return {
            "success": True,
            "message": f"Order {order_id} details fetched",
            "intent": "order.details",
            "data": order,
        }

    if ("change" in m or "update" in m) and "address" in m:
        order_id = ''.join(ch for ch in message if ch.isdigit())
        
        # If no order ID mentioned, use the user's most recent order
        if not order_id:
            recent_orders = store.list_user_orders(user_id)
            if not recent_orders:
                return {
                    "success": False,
                    "message": "No orders found. Please place an order first or specify an order ID.",
                    "intent": "order.update_address",
                    "data": {},
                }
            order = recent_orders[-1]  # Get most recent
            order_id = order["order_id"]
        else:
            order = store.get_order(order_id)
        
        if not order or order["user_id"] != user_id:
            return {
                "success": False,
                "message": f"Order {order_id} not found or not yours",
                "intent": "order.update_address",
                "data": {},
            }
        if order.get("status") in ("Shipped", "Delivered"):
            return {
                "success": False,
                "message": f"Order {order_id} is already {order['status']}. Address cannot be changed.",
                "intent": "order.update_address",
                "data": {},
            }
        # Extract address from message - look for common patterns
        new_address = message
        if " to " in new_address.lower():
            new_address = new_address.split(" to ")[-1].strip()
        elif " is " in new_address.lower():
            new_address = new_address.split(" is ")[-1].strip()
        elif "address:" in new_address.lower():
            new_address = new_address.split("address:")[-1].strip()
        else:
            new_address = new_address.replace(f"order {order_id}", "").strip()
        
        # Validate that we got a real address (not just keywords)
        keywords = ["change", "delivery", "address", "update", "my", "the", "please"]
        new_address_lower = new_address.lower()
        word_count = len([w for w in new_address_lower.split() if w not in keywords])
        
        if word_count < 2:
            return {
                "success": False,
                "message": f"Please provide the new delivery address. Example: 'Change delivery address to 42 Main Street'",
                "intent": "order.update_address",
                "data": {},
            }
        
        order["address"] = new_address
        store.update_order(order_id, order)
        return {
            "success": True,
            "message": f"Delivery address for order {order_id} updated to: {order['address']}",
            "intent": "order.update_address",
            "data": {"order_id": order_id, "new_address": order["address"]},
        }

    if ("update" in m or "change" in m) and "quantity" in m and "order" in m:
        order_id = ''.join(ch for ch in message if ch.isdigit())
        order = store.get_order(order_id)
        if not order or order["user_id"] != user_id:
            return {
                "success": False,
                "message": f"Order {order_id} not found",
                "intent": "order.update_qty",
                "data": {},
            }
        if order.get("status") not in ("Processing",):
            return {
                "success": False,
                "message": f"Order {order_id} is {order.get('status')} and cannot be updated",
                "intent": "order.update_qty",
                "data": {},
            }
        return {
            "success": True,
            "message": f"Quantity update requested for order {order_id}. Please contact support with new quantity.",
            "intent": "order.update_qty",
            "data": {"order_id": order_id},
        }

    if "cancel order" in m:
        order_id = ''.join(ch for ch in message if ch.isdigit())
        order = store.get_order(order_id)
        if not order or order["user_id"] != user_id:
            return {
                "success": False,
                "message": f"Order {order_id} not found",
                "intent": "order.cancel",
                "data": {},
            }
        order["status"] = "Cancelled"
        store.update_order(order_id, order)
        return {
            "success": True,
            "message": f"Order {order_id} cancelled",
            "intent": "order.cancel",
            "data": {"order_id": order_id, "status": "Cancelled"},
        }

    if "create" in m and "account" in m or "new account" in m or "sign up" in m or "signup" in m:
        return {
            "success": True,
            "message": "To create an account, say: Register me with name <your name> and email <your email>",
            "intent": "user.register_prompt",
            "data": {},
        }

    if "register" in m and "email" in m:
        email = None
        for token in message.replace(",", " ").split():
            if "@" in token:
                email = token.strip(".,")
                break
        if not email:
            return {
                "success": False,
                "message": "Please provide a valid email",
                "intent": "user.register",
                "data": {},
            }
        new_id = store.next_user_id()
        user_payload = {
            "user_id": new_id,
            "name": "Demo User",
            "email": email,
            "address": "Not set",
        }
        store.create_user(user_payload)
        return {
            "success": True,
            "message": "User registered",
            "intent": "user.register",
            "data": user_payload,
        }

    if "profile" in m or "registered address" in m or "order history" in m:
        user = store.get_user(user_id)
        if not user:
            return {
                "success": False,
                "message": "User not found",
                "intent": "user.details",
                "data": {},
            }
        history = store.list_user_orders(user_id)
        return {
            "success": True,
            "message": "User details fetched",
            "intent": "user.details",
            "data": {"profile": user, "orders": history},
        }

    if "how can i" in m or "how do i" in m or "how to" in m:
        return answer_knowledge_query(domain="ecommerce", query=message)

    return {
        "success": False,
        "message": "I could not map this ecommerce request yet",
        "intent": "unknown",
        "data": {},
    }
