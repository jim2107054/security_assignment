"""
Controlled DoS & DDoS Simulation Lab - Target Web Server
File: app_target_server.py
Description: A lightweight Flask dummy web server with deliberately constrained
             concurrency capacity to safely demonstrate application-layer resource
             exhaustion on localhost (127.0.0.1).
"""

import threading
import time
from flask import Flask, jsonify, render_template_string

app = Flask(__name__)

# Deliberately constrained server capacity for educational simulation
CAPACITY = 4
PROCESSING_TIME = 0.25  # Simulated processing duration per request in seconds

# Concurrency control & metrics
slots = threading.BoundedSemaphore(CAPACITY)
stats = {"accepted": 0, "rejected": 0}
lock = threading.Lock()

HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Controlled Security Lab Demo Server</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #0f172a;
            color: #f8fafc;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
        }
        .card {
            background: #1e293b;
            padding: 2.5rem;
            border-radius: 12px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.5);
            max-width: 520px;
            border: 1px solid #334155;
        }
        h1 { color: #38bdf8; margin-top: 0; }
        p { line-height: 1.6; color: #94a3b8; }
        .badge {
            display: inline-block;
            background: #0369a1;
            color: #e0f2fe;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.85rem;
            font-weight: bold;
        }
        .btn-group { margin-top: 1.5rem; display: flex; gap: 10px; }
        a.btn {
            text-decoration: none;
            background: #2563eb;
            color: white;
            padding: 0.6rem 1.2rem;
            border-radius: 6px;
            font-weight: 500;
            transition: background 0.2s;
        }
        a.btn:hover { background: #1d4ed8; }
        .footer { margin-top: 2rem; font-size: 0.8rem; color: #64748b; }
    </style>
</head>
<body>
    <div class="card">
        <span class="badge">Safe Localhost Target (127.0.0.1)</span>
        <h1>Dummy Web Server</h1>
        <p>This dummy application server models finite resource handling. It accepts a maximum of <strong>4 concurrent requests</strong>, each requiring <strong>0.25s</strong> of simulated processing time.</p>
        <div class="btn-group">
            <a class="btn" href="/work" target="_blank">Execute Workload (/work)</a>
            <a class="btn" style="background: #475569;" href="/stats" target="_blank">View Stats (/stats)</a>
        </div>
        <div class="footer">
            Coursework: Controlled Application-Layer Availability & Resource Exhaustion Demonstration.
        </div>
    </div>
</body>
</html>
"""


@app.get("/")
def home():
    """Serves the dummy landing page."""
    return render_template_string(HTML_PAGE)


@app.get("/work")
def work():
    """
    Capacity-constrained workload endpoint.
    Attempts non-blocking acquisition of a concurrency semaphore slot.
    Returns 200 OK if a slot is available, or 503 Busy if capacity is exhausted.
    """
    acquired = slots.acquire(blocking=False)
    if not acquired:
        with lock:
            stats["rejected"] += 1
        return jsonify({
            "status": "busy",
            "message": "Server capacity is currently full (HTTP 503)"
        }), 503

    try:
        time.sleep(PROCESSING_TIME)
        with lock:
            stats["accepted"] += 1
        return jsonify({
            "status": "ok",
            "message": "Request processed successfully (HTTP 200)"
        }), 200
    finally:
        slots.release()


@app.get("/stats")
def get_stats():
    """Returns real-time accepted and rejected request statistics."""
    with lock:
        return jsonify({
            "capacity": CAPACITY,
            "simulated_processing_time_sec": PROCESSING_TIME,
            "accepted_requests": stats["accepted"],
            "rejected_requests": stats["rejected"],
            "total_requests": stats["accepted"] + stats["rejected"]
        })


@app.get("/reset")
def reset_stats():
    """Utility endpoint to reset metrics counters between experimental phases."""
    with lock:
        stats["accepted"] = 0
        stats["rejected"] = 0
    return jsonify({"status": "reset", "message": "Statistics counters cleared"})


if __name__ == "__main__":
    print("=" * 60)
    print(" [TARGET SERVER] Starting Controlled Security Lab Server")
    print(f" [CONFIG] Host: 127.0.0.1 | Port: 5000 | Concurrency Capacity: {CAPACITY}")
    print("=" * 60)
    app.run(host="127.0.0.1", port=5000, threaded=True)
