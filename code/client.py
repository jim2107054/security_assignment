import time
import requests

URL = "http://127.0.0.1:5000/work"
REQUESTS = 80
DELAY = 0.01

success = 0
busy = 0
errors = 0

for i in range(REQUESTS):
    try:
        r = requests.get(URL, timeout=2)
        if r.status_code == 200:
            success += 1
        elif r.status_code == 503:
            busy += 1
        else:
            errors += 1
    except requests.RequestException:
        errors += 1
    if DELAY:
        time.sleep(DELAY)

print("\n--- CONTROLLED DoS SIMULATION ---")
print("Total requests:", REQUESTS)
print("HTTP 200:", success)
print("HTTP 503 (busy):", busy)
print("Other/errors:", errors)
