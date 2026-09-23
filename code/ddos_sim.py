import multiprocessing as mp
import requests
import time

URL = "http://127.0.0.1:5000/work"
WORKERS = 4
REQUESTS_PER_WORKER = 25
DELAY = 0.01


def worker(worker_id):
    ok = busy = errors = 0
    for _ in range(REQUESTS_PER_WORKER):
        try:
            r = requests.get(URL, timeout=2)
            if r.status_code == 200:
                ok += 1
            elif r.status_code == 503:
                busy += 1
            else:
                errors += 1
        except requests.RequestException:
            errors += 1
        time.sleep(DELAY)
    return worker_id, ok, busy, errors


if __name__ == "__main__":
    with mp.Pool(WORKERS) as pool:
        results = pool.map(worker, range(1, WORKERS + 1))
    print("\n--- DDoS-STYLE LOCAL SIMULATION ---")
    total_ok = total_busy = total_errors = 0
    for worker_id, ok, busy, errors in results:
        print(f"Worker {worker_id}: 200={ok}, 503={busy}, errors={errors}")
        total_ok += ok
        total_busy += busy
        total_errors += errors
    print("\nTotals")
    print("HTTP 200:", total_ok)
    print("HTTP 503:", total_busy)
    print("Errors:", total_errors)
