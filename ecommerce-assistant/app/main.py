from dotenv import load_dotenv
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse

from app.models.schemas import ChatRequest, ChatResponse
from app.services.firestore_service import store
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
            --bg-a: #f7fafc;
            --bg-b: #e6fffa;
            --panel: #ffffff;
            --line: #d1d5db;
            --text: #1f2937;
            --muted: #6b7280;
            --brand: #0f766e;
            --brand-strong: #0b5a55;
            --assistant-bubble: #eefbf7;
            --user-bubble: #e3f2ff;
            --danger: #b91c1c;
        }

        * { box-sizing: border-box; }

        body {
            margin: 0;
            min-height: 100vh;
            font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
            color: var(--text);
            background:
                radial-gradient(1000px 450px at 8% -10%, #b5f5ec 10%, transparent 70%),
                radial-gradient(850px 420px at 92% 0%, #bae6fd 10%, transparent 70%),
                linear-gradient(180deg, var(--bg-a), var(--bg-b));
            padding: 18px;
        }

        .shell {
            width: min(980px, 100%);
            margin: 0 auto;
            border: 1px solid var(--line);
            border-radius: 20px;
            background: rgba(255, 255, 255, 0.9);
            backdrop-filter: blur(8px);
            box-shadow: 0 18px 50px rgba(17, 24, 39, 0.12);
            overflow: hidden;
        }

        .header {
            padding: 18px 22px 10px;
            border-bottom: 1px solid #e5e7eb;
            background: linear-gradient(180deg, #ffffff, #f8fffd);
        }

        .title {
            margin: 0;
            font-size: 1.9rem;
            letter-spacing: -0.02em;
        }

        .subtitle {
            margin: 6px 0 0;
            color: var(--muted);
            font-size: 1rem;
        }

        .body {
            padding: 16px;
            display: grid;
            grid-template-columns: 1fr;
            gap: 12px;
        }

        .meta {
            display: grid;
            grid-template-columns: 1fr;
            gap: 6px;
        }

        .meta label {
            font-size: 0.9rem;
            color: var(--muted);
        }

        .meta-help {
            color: var(--muted);
            font-size: 0.82rem;
        }

        input, textarea, button {
            font: inherit;
            border: 1px solid var(--line);
            border-radius: 12px;
            outline: none;
            transition: border-color 0.2s ease, box-shadow 0.2s ease;
        }

        input, textarea {
            width: 100%;
            padding: 11px 12px;
            background: #fff;
        }

        input:focus, textarea:focus {
            border-color: #6ee7b7;
            box-shadow: 0 0 0 4px rgba(16, 185, 129, 0.16);
        }

        .chat-area {
            border: 1px solid #dbe1e7;
            border-radius: 16px;
            background: #fcfffe;
            display: flex;
            flex-direction: column;
            height: min(58vh, 520px);
            min-height: 380px;
        }

        .stream {
            flex: 1;
            overflow: auto;
            padding: 14px;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }

        .msg {
            max-width: 82%;
            padding: 11px 13px;
            border-radius: 14px;
            line-height: 1.45;
            white-space: pre-wrap;
            box-shadow: 0 5px 16px rgba(17, 24, 39, 0.08);
        }

        .msg.user {
            align-self: flex-end;
            border: 1px solid #93c5fd;
            background: linear-gradient(135deg, var(--user-bubble), #dbeafe);
        }

        .msg.assistant {
            align-self: flex-start;
            border: 1px solid #99f6e4;
            background: linear-gradient(135deg, var(--assistant-bubble), #d1fae5);
        }

        .domain {
            align-self: flex-start;
            margin-top: -3px;
            color: #065f46;
            font-size: 0.8rem;
            font-weight: 600;
        }

        .composer {
            border-top: 1px solid #e5e7eb;
            padding: 12px;
            display: grid;
            grid-template-columns: 1fr auto;
            gap: 10px;
            align-items: end;
        }

        .composer textarea {
            resize: vertical;
            min-height: 74px;
            max-height: 180px;
        }

        #send {
            min-width: 140px;
            height: 46px;
            border: none;
            cursor: pointer;
            color: #fff;
            font-weight: 700;
            letter-spacing: 0.01em;
            background: linear-gradient(135deg, var(--brand), #14b8a6);
            box-shadow: 0 10px 20px rgba(15, 118, 110, 0.25);
        }

        #send:hover:not(:disabled) {
            transform: translateY(-1px);
            background: linear-gradient(135deg, var(--brand-strong), #0f9a8d);
        }

        #send:disabled {
            cursor: not-allowed;
            opacity: 0.7;
        }

        .status {
            min-height: 20px;
            color: var(--muted);
            font-size: 0.88rem;
        }

        .status.error {
            color: var(--danger);
        }

        @media (max-width: 720px) {
            body { padding: 10px; }
            .title { font-size: 1.5rem; }
            .chat-area { min-height: 350px; height: 65vh; }
            .composer { grid-template-columns: 1fr; }
            #send { width: 100%; }
            .msg { max-width: 92%; }
        }
    </style>
</head>
<body>
    <main class="shell">
        <section class="header">
            <h1 class="title">Agentic Multi-Domain Assistant</h1>
            <p class="subtitle">Conversational workflow for Ecommerce, Travel, and Healthcare.</p>
        </section>

        <section class="body">
            <div class="meta">
                <label for="user">User ID</label>
                <input id="user" value="u1001" placeholder="u1001 (demo)" />
                <div class="meta-help">Leave empty to use demo account u1001.</div>
            </div>

            <section class="chat-area" aria-live="polite">
                <div id="stream" class="stream"></div>

                <div id="chat-form" class="composer">
                    <textarea id="message" placeholder="Type a message and press Enter. Use Shift+Enter for a new line."></textarea>
                    <button id="send" type="button">Send</button>
                </div>
            </section>

            <div id="status" class="status"></div>
        </section>
    </main>

    <script>
        (function () {
            if (window.location.href.endsWith('/?')) {
                window.history.replaceState({}, document.title, window.location.href.slice(0, -1));
            }

            var streamEl = document.getElementById("stream");
            var userEl = document.getElementById("user");
            var messageEl = document.getElementById("message");
            var sendBtn = document.getElementById("send");
            var formEl = document.getElementById("chat-form");
            var statusEl = document.getElementById("status");
            var inFlight = false;

            function setStatus(text, isError) {
                statusEl.textContent = text || "";
                statusEl.className = isError ? "status error" : "status";
            }

            function pushMessage(role, text, detectedDomain) {
                var bubble = document.createElement("div");
                bubble.className = "msg " + role;
                bubble.textContent = String(text || "");
                streamEl.appendChild(bubble);

                if (role === "assistant" && detectedDomain) {
                    var domain = document.createElement("div");
                    domain.className = "domain";
                    domain.textContent = "Detected domain: " + detectedDomain;
                    streamEl.appendChild(domain);
                }

                streamEl.scrollTop = streamEl.scrollHeight;
            }

            function showWelcomeIfEmpty() {
                if (streamEl.children.length > 0) return;
                pushMessage("assistant", "Hi! Ask about ecommerce, travel, or healthcare and I will auto-detect the right domain.");
            }

            async function loadHistory() {
                var userId = (userEl.value || "").trim() || "u1001";
                streamEl.innerHTML = "";
                showWelcomeIfEmpty();
                setStatus("Loading previous chats...", false);
                try {
                    var response = await fetch("/history/" + encodeURIComponent(userId) + "?limit=80");
                    if (!response.ok) {
                        throw new Error("Unable to load history (" + response.status + ")");
                    }
                    var payload = await response.json();
                    var messages = Array.isArray(payload.messages) ? payload.messages : [];
                    if (messages.length) {
                        streamEl.innerHTML = "";
                        messages.forEach(function (item) {
                            pushMessage(item.role || "assistant", item.text || "", item.detected_domain || "");
                        });
                    }
                    setStatus("", false);
                } catch (err) {
                    setStatus("Could not load previous chats.", true);
                    showWelcomeIfEmpty();
                }
            }

            function removePendingBubble() {
                var pending = document.getElementById("pending-assistant");
                if (pending && pending.parentNode) {
                    pending.parentNode.removeChild(pending);
                }
            }

            function addPendingBubble() {
                removePendingBubble();
                var pending = document.createElement("div");
                pending.id = "pending-assistant";
                pending.className = "msg assistant";
                pending.textContent = "Thinking...";
                streamEl.appendChild(pending);
                streamEl.scrollTop = streamEl.scrollHeight;
            }

            function formatResponse(data) {
                var lines = [];
                lines.push(data.message || "No message returned.");
                if (data.intent) lines.push("Intent: " + data.intent);

                var payload = data.data || {};

                if (Array.isArray(payload.coupons) && payload.coupons.length) {
                    lines.push("");
                    lines.push("Coupons:");
                    payload.coupons.forEach(function (c) {
                        lines.push("- " + c.code + ": " + c.description + " (" + c.status + ")");
                    });
                }

                if (payload.order_id) {
                    lines.push("");
                    lines.push("Order " + payload.order_id + ": " + (payload.status || "unknown"));
                }

                if (Array.isArray(payload.results) && payload.results.length) {
                    lines.push("");
                    lines.push("Results:");
                    payload.results.forEach(function (r) {
                        lines.push("- " + (r.flight_id || "Flight") + ": " + (r.from || "") + " to " + (r.to || "") + " (" + (r.price || "N/A") + ")");
                    });
                }

                if (Array.isArray(payload.doctors) && payload.doctors.length) {
                    lines.push("");
                    lines.push("Doctors:");
                    payload.doctors.forEach(function (d) {
                        lines.push("- Dr. " + d.name + " (" + (d.specialty || "General") + ")");
                    });
                }

                if (Array.isArray(payload.sources) && payload.sources.length) {
                    lines.push("");
                    lines.push("Reference: " + payload.sources[0]);
                }

                return lines.join("\\n");
            }

            async function submitChat() {
                if (inFlight) return;

                var message = (messageEl.value || "").trim();
                var userId = (userEl.value || "").trim() || "u1001";

                if (!message) {
                    setStatus("Please enter a message.", true);
                    messageEl.focus();
                    return;
                }

                setStatus("", false);
                pushMessage("user", message);
                messageEl.value = "";

                inFlight = true;
                sendBtn.disabled = true;
                sendBtn.textContent = "Sending...";
                setStatus("Assistant is thinking...", false);
                addPendingBubble();

                try {
                    var timeoutPromise = new Promise(function (_, reject) {
                        setTimeout(function () {
                            reject(new Error("Request timed out. Please try again."));
                        }, 25000);
                    });

                    var fetchPromise = fetch("/chat", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({
                            domain: "auto",
                            user_id: userId,
                            message: message,
                        }),
                    });

                    var response = await Promise.race([fetchPromise, timeoutPromise]);

                    if (!response.ok) {
                        var errorText = await response.text();
                        throw new Error("HTTP " + response.status + ": " + errorText);
                    }

                    var data = await response.json();
                    var rendered = formatResponse(data);
                    var detected = data && data.data ? data.data.detected_domain : "auto";

                    removePendingBubble();
                    pushMessage("assistant", rendered, detected);
                    setStatus("", false);
                } catch (err) {
                    var msg = "Request failed. " + (err && err.message ? err.message : String(err));
                    setStatus(msg, true);
                    removePendingBubble();
                    pushMessage("assistant", msg);
                } finally {
                    inFlight = false;
                    sendBtn.disabled = false;
                    sendBtn.textContent = "Send";
                    messageEl.focus();
                }
            }

            sendBtn.addEventListener("click", function () {
                submitChat();
            });

            formEl.addEventListener("submit", function (event) {
                event.preventDefault();
                return false;
            });

            window.submitChat = submitChat;

            messageEl.addEventListener("keydown", function (event) {
                if (event.key === "Enter" && !event.shiftKey) {
                    event.preventDefault();
                    submitChat();
                }
            });

            userEl.addEventListener("change", function () {
                loadHistory();
            });

            messageEl.focus();
            loadHistory();
        })();
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


@app.get("/history/{user_id}")
def history(user_id: str, limit: int = 50) -> dict:
    safe_limit = max(1, min(limit, 200))
    return {
        "success": True,
        "messages": store.list_chat_messages(user_id=user_id, limit=safe_limit),
    }


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    result = dispatch(domain=req.domain, message=req.message, user_id=req.user_id)
    detected_domain = ""
    if isinstance(result.get("data"), dict):
        detected_domain = str(result["data"].get("detected_domain", ""))

    store.save_chat_message(user_id=req.user_id, role="user", text=req.message, detected_domain=detected_domain)
    store.save_chat_message(
        user_id=req.user_id,
        role="assistant",
        text=str(result.get("message", "")),
        detected_domain=detected_domain,
    )

    return ChatResponse(
        success=result["success"],
        message=result["message"],
        data=result.get("data"),
        intent=result.get("intent"),
    )
