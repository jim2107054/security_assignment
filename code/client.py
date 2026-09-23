import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

URL = "http://127.0.0.1:5000/work"
REQUESTS = 80
CONCURRENCY = 8  # Concurrency from single client to exceed server capacity


def send_request(req_id):
    t0 = time.perf_counter()
    try:
        r = requests.get(URL, timeout=2.5)
        elapsed = (time.perf_counter() - t0) * 1000
        return req_id, r.status_code, elapsed, None
    except requests.RequestException as e:
        elapsed = (time.perf_counter() - t0) * 1000
        return req_id, 0, elapsed, str(e)


if __name__ == "__main__":
    success = 0
    busy = 0
    errors = 0

    print("=" * 60)
    print(" [STAGE B: CONTROLLED DoS SIMULATION (Single Generator)]")
    print(f" Target Endpoint: {URL}")
    print(f" Request Flood Count: {REQUESTS} | Concurrency: {CONCURRENCY}")
    print("=" * 60)

    with ThreadPoolExecutor(max_workers=CONCURRENCY) as pool:
        futures = [pool.submit(send_request, i + 1) for i in range(REQUESTS)]
        for f in as_completed(futures):
            req_id, status, elapsed, err = f.result()
            if status == 200:
                success += 1
                print(f" [DoS Stream] Req #{req_id:02d}/{REQUESTS} -> HTTP 200 [OK] ({elapsed:.1f} ms)")
            elif status == 503:
                busy += 1
                print(f" [DoS Stream] Req #{req_id:02d}/{REQUESTS} -> HTTP 503 [BUSY - REJECTED] ({elapsed:.1f} ms)")
            else:
                errors += 1
                print(f" [DoS Stream] Req #{req_id:02d}/{REQUESTS} -> ERROR: {err}")

    print("\n--- CONTROLLED DoS SIMULATION ---")
    print("Total requests:", REQUESTS)
    print("HTTP 200:", success)
    print("HTTP 503 (busy):", busy)
    print("Other/errors:", errors)
