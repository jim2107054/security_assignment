from flask import Flask, jsonify
import threading
import time

app = Flask(__name__)

# Deliberately small capacity for the classroom simulation.
CAPACITY = 4
PROCESSING_TIME = 0.25

slots = threading.BoundedSemaphore(CAPACITY)
stats = {"accepted": 0, "rejected": 0}
lock = threading.Lock()


@app.get("/")
def home():
    return """
    <html>
    <head><title>Security Lab Demo</title></head>
    <body>
    <h1>My Security Lab Website</h1>
    <p>This is a controlled localhost DoS/DDoS simulation.</p>
    <p>Try: <a href="/work">/work</a></p>
    </body>
    </html>
    """


@app.get("/work")
def work():
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


@app.get("/stats")
def get_stats():
    with lock:
        return jsonify(stats)


if __name__ == "__main__":
    # Localhost only - do not change this to 0.0.0.0.
    app.run(host="127.0.0.1", port=5000, threaded=True)
