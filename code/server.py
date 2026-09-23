from flask import Flask, jsonify, render_template_string
import threading
import time

app = Flask(__name__)

# Deliberately constrained server capacity for the classroom simulation.
CAPACITY = 4
PROCESSING_TIME = 0.25  # Simulated processing duration per work request in seconds

slots = threading.BoundedSemaphore(CAPACITY)
stats = {"accepted": 0, "rejected": 0, "health_checks": 0}
lock = threading.Lock()

HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Security Lab: DoS & DDoS Availability Test</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background: #0f172a; color: #f8fafc; display: flex; justify-content: center; align-items: center; min-height: 100vh; padding: 20px; }
        .card { background: #1e293b; border: 1px solid #334155; border-radius: 16px; padding: 32px; max-width: 580px; width: 100%; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5); }
        .badge { display: inline-block; padding: 4px 12px; background: rgba(56, 189, 248, 0.15); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.3); border-radius: 9999px; font-size: 12px; font-weight: 600; margin-bottom: 16px; }
        h1 { font-size: 24px; font-weight: 700; color: #ffffff; margin-bottom: 8px; }
        p.subtitle { color: #94a3b8; font-size: 14px; line-height: 1.5; margin-bottom: 24px; }
        .status-box { padding: 20px; border-radius: 12px; text-align: center; margin-bottom: 24px; transition: all 0.3s ease; border: 1px solid transparent; }
        .status-idle { background: #0f172a; border-color: #334155; color: #94a3b8; }
        .status-online { background: rgba(34, 197, 94, 0.15); border-color: rgba(34, 197, 94, 0.4); color: #4ade80; }
        .status-overloaded { background: rgba(239, 68, 68, 0.15); border-color: rgba(239, 68, 68, 0.4); color: #f87171; }
        .status-title { font-size: 18px; font-weight: 700; margin-bottom: 4px; }
        .status-desc { font-size: 13px; opacity: 0.9; }
        .btn-check { width: 100%; padding: 14px 20px; background: #2563eb; color: #ffffff; font-size: 15px; font-weight: 600; border: none; border-radius: 10px; cursor: pointer; transition: background 0.2s; box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.3); }
        .btn-check:hover { background: #1d4ed8; }
        .btn-check:active { transform: scale(0.99); }
        .info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 24px; padding-top: 20px; border-top: 1px solid #334155; font-size: 13px; color: #94a3b8; }
        .info-item span { color: #f1f5f9; font-weight: 600; }
    </style>
</head>
<body>
    <div class="card">
        <span class="badge">Controlled Localhost Simulation &bull; 127.0.0.1:5000</span>
        <h1>Dummy Web Server</h1>
        <p class="subtitle">This page represents a legitimate browser client. Press <strong>Check Server</strong> to probe availability under normal and high load conditions.</p>
        
        <div id="statusBox" class="status-box status-idle">
            <div id="statusTitle" class="status-title">READY TO TEST</div>
            <div id="statusDesc" class="status-desc">Click button below to test server availability.</div>
        </div>

        <button class="btn-check" id="checkBtn" onclick="checkHealth()">Check Server (GET /health)</button>

        <div class="info-grid">
            <div class="info-item">Capacity: <span>4 Active Slots</span></div>
            <div class="info-item">Work Delay: <span>0.25s per request</span></div>
            <div class="info-item">Health Endpoint: <span>/health</span></div>
            <div class="info-item">Workload Endpoint: <span>/work</span></div>
        </div>
    </div>

    <script>
        async function checkHealth() {
            const btn = document.getElementById('checkBtn');
            const box = document.getElementById('statusBox');
            const title = document.getElementById('statusTitle');
            const desc = document.getElementById('statusDesc');
            
            btn.disabled = true;
            btn.innerText = 'Probing Server...';
            
            const startTime = performance.now();
            try {
                const response = await fetch('/health', { cache: 'no-store' });
                const elapsed = Math.round(performance.now() - startTime);
                
                if (response.status === 200) {
                    box.className = 'status-box status-online';
                    title.innerText = 'SERVER ONLINE';
                    desc.innerText = 'HTTP 200 OK &bull; Response time: ' + elapsed + ' ms &bull; Server is healthy.';
                } else if (response.status === 503) {
                    box.className = 'status-box status-overloaded';
                    title.innerText = 'SERVER OVERLOADED';
                    desc.innerText = 'HTTP 503 Service Unavailable &bull; Server capacity currently exhausted!';
                } else {
                    box.className = 'status-box status-overloaded';
                    title.innerText = 'SERVER ERROR (HTTP ' + response.status + ')';
                    desc.innerText = 'Unexpected response received from server.';
                }
            } catch (err) {
                box.className = 'status-box status-overloaded';
                title.innerText = 'SERVER UNAVAILABLE';
                desc.innerText = 'Connection timed out or network error: ' + err.message;
            } finally {
                btn.disabled = false;
                btn.innerText = 'Check Server (GET /health)';
            }
        }
    </script>
</body>
</html>
"""


@app.route("/", methods=["GET"])
def home():
    """Serves the interactive web client."""
    return render_template_string(HTML_PAGE)


@app.route("/health", methods=["GET"])
def health():
    """
    Legitimate client health check endpoint.
    Attempts non-blocking slot acquisition. Returns 200 OK if available,
    or 503 Busy if all 4 concurrency slots are occupied by /work queries.
    """
    acquired = slots.acquire(blocking=False)
    if not acquired:
        with lock:
            stats["rejected"] += 1
        return jsonify({
            "status": "busy",
            "message": "Server capacity is currently full"
        }), 503

    try:
        with lock:
            stats["health_checks"] += 1
        return jsonify({
            "status": "ok",
            "message": "Server is healthy"
        }), 200
    finally:
        slots.release()


@app.route("/work", methods=["GET"])
def work():
    """
    Expensive simulated workload endpoint used by traffic generators.
    Sleeps for PROCESSING_TIME (0.25s) to consume a worker slot.
    """
    acquired = slots.acquire(blocking=False)
    if not acquired:
        with lock:
            stats["rejected"] += 1
        return jsonify({
            "status": "busy",
            "message": "Server capacity is currently full"
        }), 503

    try:
        time.sleep(PROCESSING_TIME)
        with lock:
            stats["accepted"] += 1
        return jsonify({
            "status": "ok",
            "message": "Request processed"
        }), 200
    finally:
        slots.release()


@app.route("/stats", methods=["GET"])
def get_stats():
    """Returns real-time accepted, rejected, and health check statistics."""
    with lock:
        return jsonify({
            "capacity": CAPACITY,
            "processing_time": PROCESSING_TIME,
            "accepted_workload": stats["accepted"],
            "rejected_requests": stats["rejected"],
            "successful_health_checks": stats["health_checks"]
        })


if __name__ == "__main__":
    # Localhost only - do not change this to 0.0.0.0
    app.run(host="127.0.0.1", port=5000, threaded=True)
