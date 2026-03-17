from dotenv import load_dotenv
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse

from app.models.schemas import ChatRequest, ChatResponse
from app.tools.dispatcher import dispatch

load_dotenv()

app = FastAPI(title="Agentic Multi-Domain Assistant", version="0.1.0")


DEMO_UI_HTML = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Agentic Multi-Domain Assistant</title>
    <style>
        :root {
            --bg: #f4f8f7;
            --card: #ffffff;
            --text: #1f2937;
            --muted: #6b7280;
            --brand: #0f766e;
            --brand-2: #14b8a6;
            --border: #d1d5db;
        }
        * { box-sizing: border-box; }
        body {
            margin: 0;
            font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
            background: radial-gradient(circle at 10% 10%, #ccfbf1 0%, var(--bg) 45%);
            color: var(--text);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 900px;
            margin: 0 auto;
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 22px;
            box-shadow: 0 12px 30px rgba(15, 118, 110, 0.12);
        }
        h1 {
            margin: 0 0 8px;
            font-size: 1.5rem;
        }
        .sub {
            color: var(--muted);
            margin-bottom: 14px;
        }
        .row {
            display: grid;
            grid-template-columns: 1fr;
            gap: 10px;
            margin-bottom: 10px;
        }
        @media (max-width: 700px) {
            .row { grid-template-columns: 1fr; }
        }
        label {
            display: block;
            font-size: 0.9rem;
            color: var(--muted);
            margin-bottom: 4px;
        }
        input, select, textarea, button {
            width: 100%;
            font: inherit;
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 10px 12px;
            background: #fff;
        }
        textarea { min-height: 100px; resize: vertical; }
        #send {
            background: linear-gradient(135deg, var(--brand), var(--brand-2));
            border: none;
            color: #fff;
            font-weight: 600;
            cursor: pointer;
            margin-top: 10px;
            padding: 12px;
            font-size: 1.05rem;
            transition: all 0.3s ease;
        }
        #send:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 8px 16px rgba(15, 118, 110, 0.3);
        }
        #send:active:not(:disabled) {
            transform: translateY(0);
        }
        #send:disabled { opacity: 0.7; cursor: not-allowed; }
        .chips { display: flex; flex-wrap: wrap; gap: 8px; margin: 12px 0; }
        .chip {
            width: auto;
            flex: 0 0 auto;
            border: 1px solid #99f6e4;
            color: #115e59;
            background: #f0fdfa;
            border-radius: 999px;
            padding: 8px 12px;
            font-size: 0.85rem;
            cursor: pointer;
            font-weight: 600;
        }
        .chip:hover { background: #ccfbf1; }
        .out {
            margin-top: 14px;
            border: 1px dashed var(--border);
            border-radius: 10px;
            background: #fafafa;
            padding: 12px;
            font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
            min-height: 120px;
            max-height: 340px;
            overflow-y: auto;
        }
        .bubble {
            margin: 8px 0;
            padding: 10px 12px;
            border-radius: 10px;
            white-space: pre-wrap;
            line-height: 1.35;
        }
        .bubble.user {
            background: #e0f2fe;
            border: 1px solid #bae6fd;
        }
        .bubble.assistant {
            background: #ecfeff;
            border: 1px solid #99f6e4;
        }
        .meta-line {
            margin-top: 4px;
            color: #0f766e;
            font-size: 0.82rem;
            font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Agentic Multi-Domain Assistant</h1>
        <div class="sub">Demo UI for Ecommerce, Travel, and Healthcare workflows</div>

        <form id="chat-form">
        <div class="row">
            <div>
                <label for="user">User ID</label>
                <input id="user" value="u1001" />
            </div>
        </div>

        <label for="message">Message</label>
        <textarea id="message" placeholder="Ask something like: Show available coupons"></textarea>

        <div class="chips">
            <button type="button" class="chip" data-domain="ecommerce" data-prompt="Show available coupons">Coupons</button>
            <button type="button" class="chip" data-domain="ecommerce" data-prompt="What is the status of my order 12345?">Order Status</button>
            <button type="button" class="chip" data-domain="travel" data-prompt="Search flights from Delhi to Bangalore">Flight Search</button>
            <button type="button" class="chip" data-domain="travel" data-prompt="What is the baggage limit for domestic flights?">Baggage Policy</button>
            <button type="button" class="chip" data-domain="healthcare" data-prompt="Book an appointment with Dr. Sharma tomorrow">Book Appointment</button>
            <button type="button" class="chip" data-domain="healthcare" data-prompt="What are the hospital visiting hours?">Visiting Hours</button>
        </div>

        <button id="send" type="button">Send</button>
        </form>
        <div id="output" class="out">
            <div class="bubble assistant">Hi! Ask anything about ecommerce, travel, or healthcare. I will auto-detect the domain.</div>
        </div>
    </div>

    <script>
        const messageEl = document.getElementById("message");
        const outputEl = document.getElementById("output");
        const sendBtn = document.getElementById("send");
        const formEl = document.getElementById("chat-form");

        function appendBubble(role, text, detectedDomain) {
            const wrap = document.createElement("div");
            wrap.className = "bubble " + role;
            wrap.innerHTML = String(text || "").replace(/\n/g, "<br>");

            if (role === "assistant" && detectedDomain) {
                const meta = document.createElement("div");
                meta.className = "meta-line";
                meta.textContent = "Detected domain: " + detectedDomain;
                wrap.appendChild(meta);
            }

            outputEl.appendChild(wrap);
            outputEl.scrollTop = outputEl.scrollHeight;
        }

        function formatResponse(data) {
            const lines = [];
            lines.push(data.message || "No message returned.");

            if (data.intent) {
                lines.push("Intent: " + data.intent);
            }

            const payload = data.data || {};

            // Handle coupons
            if (payload.coupons && Array.isArray(payload.coupons) && payload.coupons.length > 0) {
                lines.push("");
                lines.push("Coupons:");
                payload.coupons.forEach(function(c) {
                    lines.push("- " + c.code + ": " + c.description + " (" + c.status + ", expires " + c.expiry + ")");
                });
            }

            // Handle flights
            if (payload.results && Array.isArray(payload.results) && payload.results.length > 0) {
                lines.push("");
                lines.push("Results:");
                payload.results.forEach(function(r) {
                    if (r.flight_id) {
                        lines.push("- Flight " + r.flight_id + ": " + r.from + " to " + r.to + ", Rs " + r.price);
                    } else {
                        lines.push("- " + JSON.stringify(r));
                    }
                });
            }

            // Handle order details
            if (payload.order_id) {
                lines.push("");
                lines.push("Order Details:");
                lines.push("Order ID: " + payload.order_id);
                if (payload.status) lines.push("Status: " + payload.status);
                if (payload.delivery_date) lines.push("Delivery Date: " + payload.delivery_date);
            }

            // Handle profile
            if (payload.profile) {
                lines.push("");
                lines.push("Profile:");
                lines.push("Name: " + payload.profile.name);
                lines.push("Email: " + payload.profile.email);
                lines.push("Address: " + payload.profile.address);
                if (payload.orders && Array.isArray(payload.orders) && payload.orders.length > 0) {
                    lines.push("");
                    lines.push("Order History:");
                    payload.orders.forEach(function(ord) {
                        lines.push("- Order " + ord.order_id + ": " + ord.status + " (" + ord.total + ")");
                    });
                }
            }

            // Handle knowledge sources
            if (payload.sources && Array.isArray(payload.sources) && payload.sources.length > 0) {
                lines.push("");
                lines.push("Reference: " + payload.sources[0]);
            }

            // Handle doctors
            if (payload.doctors && Array.isArray(payload.doctors) && payload.doctors.length > 0) {
                lines.push("");
                lines.push("Doctors:");
                payload.doctors.forEach(function(d) {
                    lines.push("- Dr. " + d.name + " (" + d.specialty + "): " + d.availability);
                });
            }

            return lines.join("\n");
        }

        document.querySelectorAll(".chip").forEach((chip) => {
            chip.addEventListener("click", () => {
                messageEl.value = chip.dataset.prompt || "";
            });
        });

        async function submitChat() {
            const payload = {
                domain: "auto",
                user_id: document.getElementById("user").value,
                message: messageEl.value,
            };

            if (!payload.message.trim()) {
                appendBubble("assistant", "Please enter a message.");
                return;
            }

            appendBubble("user", payload.message);
            sendBtn.disabled = true;
            console.log('Sending payload:', payload);

            try {
                const res = await fetch("/chat", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload),
                });

                console.log('Response status:', res.status);

                if (!res.ok) {
                    const errText = await res.text();
                    console.error('Error response:', errText);
                    appendBubble("assistant", "Error " + res.status + ": " + errText);
                } else {
                    const data = await res.json();
                    console.log('Response data:', data);
                    const text = formatResponse(data);
                    const detected = data && data.data ? data.data.detected_domain : "";
                    appendBubble("assistant", text, detected);
                }
            } catch (err) {
                console.error('Request failed:', err);
                appendBubble("assistant", "Request failed: " + String(err) + "\nCheck browser console for details.");
            } finally {
                sendBtn.disabled = false;
            }
        }

        sendBtn.addEventListener("click", submitChat);
        formEl.addEventListener("submit", (event) => {
            event.preventDefault();
            submitChat();
        });
    </script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
def home() -> str:
        return DEMO_UI_HTML


@app.get("/ui", response_class=HTMLResponse)
def ui_page() -> str:
        return """
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Assistant UI Fallback</title>
    <style>
        body { font-family: "Segoe UI", Tahoma, sans-serif; margin: 24px; background: #f8fafc; }
        .card { max-width: 720px; margin: 0 auto; background: #fff; padding: 16px; border: 1px solid #d1d5db; border-radius: 12px; }
        label { display: block; margin-top: 10px; color: #4b5563; }
        input, select, textarea, button { width: 100%; padding: 10px; margin-top: 6px; border: 1px solid #d1d5db; border-radius: 8px; font: inherit; }
        textarea { min-height: 90px; }
        button { background: #0f766e; color: #fff; border: none; font-weight: 600; margin-top: 14px; }
        .hint { color: #6b7280; font-size: 0.9rem; }
    </style>
</head>
<body>
    <div class="card">
        <h2>Assistant UI (Fallback)</h2>
        <p class="hint">Use this page if the main UI is not showing responses.</p>
        <form method="post" action="/ui">
            <label>Domain</label>
            <select name="domain">
                <option value="auto" selected>Auto Detect</option>
                <option value="ecommerce">Ecommerce</option>
                <option value="travel">Travel</option>
                <option value="healthcare">Healthcare</option>
            </select>

            <label>User ID</label>
            <input type="text" name="user_id" value="u1001" />

            <label>Message</label>
            <textarea name="message" placeholder="Ask your query"></textarea>

            <button type="submit">Send</button>
        </form>
    </div>
</body>
</html>
"""


@app.post("/ui", response_class=HTMLResponse)
def ui_submit(domain: str = Form(...), user_id: str = Form(...), message: str = Form(...)) -> str:
    import html as _html
    result = dispatch(domain=domain, message=message, user_id=user_id)
    data = result.get("data") or {}

    # Build extra detail rows
    detail_rows = ""
    coupons = data.get("coupons") if isinstance(data, dict) else None
    results = data.get("results") if isinstance(data, dict) else None
    sources = data.get("sources") if isinstance(data, dict) else None
    doctors = data.get("doctors") if isinstance(data, dict) else None
    records = data.get("records") if isinstance(data, dict) else None
    bookings = data.get("bookings") if isinstance(data, dict) else None
    profile = data.get("profile") if isinstance(data, dict) else None
    orders = data.get("orders") if isinstance(data, dict) else None

    if profile:
        profile_html = f"""
        <h3>Profile Information</h3>
        <table border='1' cellpadding='6' style='border-collapse:collapse;width:100%'>
            <tr><th>Field</th><th>Value</th></tr>
            <tr><td>User ID</td><td>{_html.escape(str(profile.get('user_id','-')))}</td></tr>
            <tr><td>Name</td><td>{_html.escape(str(profile.get('name','-')))}</td></tr>
            <tr><td>Email</td><td>{_html.escape(str(profile.get('email','-')))}</td></tr>
            <tr><td>Address</td><td>{_html.escape(str(profile.get('address','-')))}</td></tr>
        </table>
        """
        if orders and len(orders) > 0:
            order_rows = "".join(
                f"<tr><td>{_html.escape(str(o.get('order_id','-')))}</td><td>{_html.escape(str(o.get('status','-')))}</td><td>{_html.escape(str(o.get('total','-')))}</td></tr>"
                for o in orders
            )
            profile_html += f"""
            <h3>Order History</h3>
            <table border='1' cellpadding='6' style='border-collapse:collapse;width:100%'>
                <tr><th>Order ID</th><th>Status</th><th>Total</th></tr>
                {order_rows}
            </table>
            """
        detail_rows = profile_html
    elif coupons:
        rows = "".join(
            f"<tr><td>{_html.escape(c.get('code',''))}</td><td>{_html.escape(c.get('description',''))}</td><td>{_html.escape(c.get('status',''))}</td><td>{_html.escape(c.get('expiry',''))}</td></tr>"
            for c in coupons
        )
        detail_rows = f"<h3>Coupons</h3><table border='1' cellpadding='6' style='border-collapse:collapse;width:100%'><tr><th>Code</th><th>Description</th><th>Status</th><th>Expiry</th></tr>{rows}</table>"
    elif results:
        rows = "".join(
            f"<tr><td>{_html.escape(str(r.get('flight_id',r.get('id','-'))))}</td><td>{_html.escape(str(r.get('from','-')))}</td><td>{_html.escape(str(r.get('to','-')))}</td><td>{_html.escape(str(r.get('price','-')))}</td></tr>"
            for r in results
        )
        detail_rows = f"<h3>Results</h3><table border='1' cellpadding='6' style='border-collapse:collapse;width:100%'><tr><th>ID</th><th>From</th><th>To</th><th>Price</th></tr>{rows}</table>"
    elif doctors:
        rows = "".join(
            f"<tr><td>{_html.escape(d.get('name',''))}</td><td>{_html.escape(', '.join(d.get('slots',[])))}</td></tr>"
            for d in doctors
        )
        detail_rows = f"<h3>Doctors</h3><table border='1' cellpadding='6' style='border-collapse:collapse;width:100%'><tr><th>Doctor</th><th>Available Slots</th></tr>{rows}</table>"
    elif records:
        rows = "".join(
            f"<tr><td>{_html.escape(r.get('date',''))}</td><td>{_html.escape(r.get('summary',''))}</td></tr>"
            for r in records
        )
        detail_rows = f"<h3>Medical Records</h3><table border='1' cellpadding='6' style='border-collapse:collapse;width:100%'><tr><th>Date</th><th>Summary</th></tr>{rows}</table>"
    elif bookings:
        rows = "".join(
            f"<tr><td>{_html.escape(b.get('booking_id',''))}</td><td>{_html.escape(b.get('status',''))}</td><td>{_html.escape(b.get('request',''))}</td></tr>"
            for b in bookings
        )
        detail_rows = f"<h3>Bookings</h3><table border='1' cellpadding='6' style='border-collapse:collapse;width:100%'><tr><th>ID</th><th>Status</th><th>Request</th></tr>{rows}</table>"
    elif sources:
        detail_rows = f"<h3>Reference</h3><div style='background:#f0fdfa;padding:10px;border-radius:8px'>{_html.escape(sources[0])}</div>"

    return f"""
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Assistant Result</title>
    <style>
        body {{ font-family: "Segoe UI", Tahoma, sans-serif; margin: 24px; background: #f8fafc; }}
        .card {{ max-width: 800px; margin: 0 auto; background: #fff; padding: 20px; border: 1px solid #d1d5db; border-radius: 12px; }}
        .msg {{ white-space: pre-wrap; background: #f9fafb; border: 1px solid #e5e7eb; padding: 10px; border-radius: 8px; font-size: 1rem; }}
        .meta {{ color: #4b5563; margin-top: 8px; font-size: 0.9rem; }}
        a {{ color: #0f766e; text-decoration: none; font-weight: 600; }}
        table {{ margin-top: 10px; font-size: 0.9rem; }}
        th {{ background: #f0fdfa; }}
    </style>
</head>
<body>
    <div class="card">
        <h2>Response</h2>
        <div class="msg">{_html.escape(result.get("message", "No message"))}</div>
        {detail_rows}
        <div class="meta">Intent: {_html.escape(result.get("intent", "unknown"))}</div>
        <div class="meta">Domain: {_html.escape(domain)} | User: {_html.escape(user_id)}</div>
        <p><a href="/ui">&larr; Ask another question</a></p>
    </div>
</body>
</html>
"""


@app.get("/health")
def health() -> dict:
    return {"ok": True, "service": "agentic-multi-domain"}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    result = dispatch(domain=req.domain, message=req.message, user_id=req.user_id)
    return ChatResponse(
        success=result["success"],
        message=result["message"],
        data=result.get("data"),
        intent=result.get("intent"),
    )
