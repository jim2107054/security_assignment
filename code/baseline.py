import time
import requests

URL = "http://127.0.0.1:5000/work"
TOTAL = 20
latencies = []
success = 0
failed = 0

for i in range(TOTAL):
    start = time.perf_counter()
    try:
        r = requests.get(URL, timeout=3)
        elapsed = (time.perf_counter() - start) * 1000
        latencies.append(elapsed)
        if r.status_code == 200:
            success += 1
        else:
            failed += 1
        print(f"{i+1:02d}: HTTP {r.status_code}, {elapsed:.1f} ms")
    except requests.RequestException as e:
        failed += 1
        print(f"{i+1:02d}: ERROR {e}")
    time.sleep(0.15)

print("\n--- BASELINE ---")
print("Requests:", TOTAL)
print("Success:", success)
print("Failed:", failed)
if latencies:
    print("Average latency: %.1f ms" % (sum(latencies) / len(latencies)))
