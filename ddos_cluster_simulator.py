"""
Controlled DoS & DDoS Simulation Lab - DDoS Cluster Simulator
File: ddos_cluster_simulator.py
Description: Simulates a Distributed Denial of Service (DDoS) attack using multiprocessing.
             Spawns 4 distinct concurrent worker processes (representing distributed client bot nodes).
             Each process sends 25 concurrent requests (100 total requests in aggregate)
             overwhelming the server's limited concurrency capacity (CAPACITY=4).
"""

import multiprocessing as mp
import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

TARGET_URL = "http://127.0.0.1:5000/work"
NUM_WORKERS = 4
REQUESTS_PER_WORKER = 25
THREADS_PER_WORKER = 4  # Concurrency per bot node


def _execute_req(url):
    t0 = time.perf_counter()
    try:
        r = requests.get(url, timeout=2.5)
        elapsed = (time.perf_counter() - t0) * 1000
        return r.status_code, elapsed, None
    except requests.RequestException as e:
        elapsed = (time.perf_counter() - t0) * 1000
        return 0, elapsed, str(e)


def simulate_bot_worker(worker_args):
    """
    Simulates an individual distributed bot/client node sending rapid concurrent requests.
    """
    worker_id, url, count, threads = worker_args
    ok_count = 0
    busy_count = 0
    error_count = 0
    latencies = []

    with ThreadPoolExecutor(max_workers=threads) as exec_pool:
        futures = [exec_pool.submit(_execute_req, url) for _ in range(count)]
        for f in as_completed(futures):
            code, elapsed, err = f.result()
            latencies.append(elapsed)
            if code == 200:
                ok_count += 1
            elif code == 503:
                busy_count += 1
            else:
                error_count += 1

    return {
        "worker_id": worker_id,
        "ok": ok_count,
        "busy": busy_count,
        "errors": error_count,
        "latencies": latencies,
        "avg_latency": (sum(latencies) / len(latencies)) if latencies else 0.0
    }


def run_ddos_simulation(url=TARGET_URL, workers=NUM_WORKERS, req_per_worker=REQUESTS_PER_WORKER, threads=THREADS_PER_WORKER):
    total_expected = workers * req_per_worker
    print("=" * 60)
    print(" [STAGE C: CONTROLLED DDoS-STYLE SIMULATION (Multi-Worker Cluster)]")
    print(f" Target Endpoint         : {url}")
    print(f" Concurrent Workers (Bots): {workers}")
    print(f" Requests Per Worker     : {req_per_worker} ({threads} threads/worker)")
    print(f" Aggregate Request Volume: {total_expected}")
    print("=" * 60)

    worker_tasks = [(wid, url, req_per_worker, threads) for wid in range(1, workers + 1)]

    start_time = time.perf_counter()
    with mp.Pool(processes=workers) as pool:
        results = pool.map(simulate_bot_worker, worker_tasks)
    total_elapsed = time.perf_counter() - start_time

    total_ok = 0
    total_busy = 0
    total_errors = 0
    all_latencies = []

    print("\n" + "-" * 25 + " PER-WORKER BREAKDOWN " + "-" * 25)
    for res in results:
        wid = res["worker_id"]
        ok = res["ok"]
        busy = res["busy"]
        err = res["errors"]
        avg_lat = res["avg_latency"]
        print(f" [Worker #{wid:02d}] -> HTTP 200: {ok:2d} | HTTP 503: {busy:2d} | Errors: {err:2d} | Avg Latency: {avg_lat:.2f} ms")
        total_ok += ok
        total_busy += busy
        total_errors += err
        all_latencies.extend(res["latencies"])

    overall_avg_lat = (sum(all_latencies) / len(all_latencies)) if all_latencies else 0.0
    min_lat = min(all_latencies) if all_latencies else 0.0
    max_lat = max(all_latencies) if all_latencies else 0.0

    print("\n" + "-" * 30 + " DDoS CLUSTER TOTALS " + "-" * 30)
    print(f" Total Requests Completed   : {len(all_latencies)}")
    print(f" Execution Duration         : {total_elapsed:.2f} s")
    print(f" Total HTTP 200 (Processed) : {total_ok} ({total_ok/total_expected*100:.1f}%)")
    print(f" Total HTTP 503 (Capacity)  : {total_busy} ({total_busy/total_expected*100:.1f}%)")
    print(f" Total Network Errors       : {total_errors} ({total_errors/total_expected*100:.1f}%)")
    print(f" Mean Latency               : {overall_avg_lat:.2f} ms")
    print(f" Latency Range (Min / Max)  : {min_lat:.2f} ms / {max_lat:.2f} ms")
    print("-" * 78)

    return {
        "stage": "DDoS Simulation",
        "workers": workers,
        "req_per_worker": req_per_worker,
        "total": total_expected,
        "duration_sec": total_elapsed,
        "success_200": total_ok,
        "busy_503": total_busy,
        "errors": total_errors,
        "latencies": all_latencies,
        "avg_latency_ms": overall_avg_lat,
        "min_latency_ms": min_lat,
        "max_latency_ms": max_lat,
        "rejection_rate_pct": (total_busy / total_expected) * 100 if total_expected else 0,
        "worker_results": results
    }


if __name__ == "__main__":
    run_ddos_simulation()
