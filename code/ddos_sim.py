import multiprocessing as mp
import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

URL = "http://127.0.0.1:5000/work"
WORKERS = 4
REQUESTS_PER_WORKER = 25
THREADS_PER_WORKER = 3


def _send_req(url):
    try:
        r = requests.get(url, timeout=2.5)
        return r.status_code
    except requests.RequestException:
        return 0


def worker(worker_id):
    ok = busy = errors = 0
    with ThreadPoolExecutor(max_workers=THREADS_PER_WORKER) as pool:
        futures = [pool.submit(_send_req, URL) for _ in range(REQUESTS_PER_WORKER)]
        for f in as_completed(futures):
            code = f.result()
            if code == 200:
                ok += 1
            elif code == 503:
                busy += 1
            else:
                errors += 1
    return worker_id, ok, busy, errors


if __name__ == "__main__":
    print("=" * 60)
    print(" [STAGE C: CONTROLLED DDoS-STYLE SIMULATION (Multi-Worker)]")
    print(f" Target Endpoint         : {URL}")
    print(f" Concurrent Bot Workers  : {WORKERS} processes")
    print(f" Requests Per Worker     : {REQUESTS_PER_WORKER} requests")
    print(f" Aggregate Request Count : {WORKERS * REQUESTS_PER_WORKER} requests")
    print("=" * 60)

    with mp.Pool(WORKERS) as pool:
        results = pool.map(worker, range(1, WORKERS + 1))

    print("\n----------------- PER-WORKER BOT CLUSTER BREAKDOWN -----------------")
    total_ok = total_busy = total_errors = 0
    for worker_id, ok, busy, errors in results:
        print(f" Worker {worker_id}: 200={ok:2d}, 503={busy:2d}, errors={errors:2d}")
        total_ok += ok
        total_busy += busy
        total_errors += errors

    print("\n----------------------- DDoS CLUSTER TOTALS ------------------------")
    print(" Aggregate Requests Sent   :", total_ok + total_busy + total_errors)
    print(" HTTP 200 (Processed)      :", total_ok)
    print(" HTTP 503 (Capacity Full)  :", total_busy)
    print(" Network Socket Errors     :", total_errors)
    print("--------------------------------------------------------------------")
