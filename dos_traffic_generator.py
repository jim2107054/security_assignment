"""
Controlled DoS & DDoS Simulation Lab - DoS Traffic Generator
File: dos_traffic_generator.py
Description: Simulates an application-layer Denial of Service (DoS) attack from a single
             client source. Uses concurrent threads to simulate high request arrival rates,
             exhausting the server's concurrency capacity (CAPACITY=4) and triggering HTTP 503 errors.
"""

import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

TARGET_URL = "http://127.0.0.1:5000/work"
REQUESTS_COUNT = 80
CONCURRENT_THREADS = 8  # Single host firing 8 concurrent streams to exceed CAPACITY=4


def send_single_request(req_id, url):
    """Dispatches a single HTTP GET request and returns metric tuple."""
    req_start = time.perf_counter()
    try:
        response = requests.get(url, timeout=2.5)
        elapsed_ms = (time.perf_counter() - req_start) * 1000
        return req_id, response.status_code, elapsed_ms, None
    except requests.RequestException as exc:
        elapsed_ms = (time.perf_counter() - req_start) * 1000
        return req_id, 0, elapsed_ms, str(exc)


def run_dos_simulation(url=TARGET_URL, total=REQUESTS_COUNT, threads=CONCURRENT_THREADS):
    print("=" * 60)
    print(" [STAGE B: CONTROLLED DoS SIMULATION (Single Host, Concurrent Streams)]")
    print(f" Target Endpoint: {url}")
    print(f" Total Requests : {total} | Concurrency Stream: {threads} threads")
    print("=" * 60)

    success_200 = 0
    busy_503 = 0
    errors = 0
    latencies = []

    start_batch_time = time.perf_counter()

    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = [executor.submit(send_single_request, i + 1, url) for i in range(total)]

        for future in as_completed(futures):
            req_id, status_code, elapsed_ms, err = future.result()
            latencies.append(elapsed_ms)

            if status_code == 200:
                success_200 += 1
                status_label = "HTTP 200 [OK]"
            elif status_code == 503:
                busy_503 += 1
                status_label = "HTTP 503 [BUSY - CAPACITY EXHAUSTED]"
            else:
                errors += 1
                status_label = f"ERROR/TIMEOUT ({err})"

            print(f" [DoS Stream] Req #{req_id:02d} -> {status_label} ({elapsed_ms:.2f} ms)")

    total_duration = time.perf_counter() - start_batch_time
    avg_latency = (sum(latencies) / len(latencies)) if latencies else 0.0
    min_latency = min(latencies) if latencies else 0.0
    max_latency = max(latencies) if latencies else 0.0

    print("\n" + "-" * 30 + " DoS TEST SUMMARY " + "-" * 30)
    print(f" Total Requests Dispatched  : {total}")
    print(f" Total Duration             : {total_duration:.2f} s")
    print(f" Requests Accepted (HTTP 200): {success_200} ({success_200/total*100:.1f}%)")
    print(f" Requests Dropped (HTTP 503) : {busy_503} ({busy_503/total*100:.1f}%)")
    print(f" Errors/Timeouts            : {errors} ({errors/total*100:.1f}%)")
    print(f" Average Latency            : {avg_latency:.2f} ms")
    print(f" Latency Range (Min / Max)  : {min_latency:.2f} ms / {max_latency:.2f} ms")
    print("-" * 78)

    return {
        "stage": "DoS Simulation",
        "total": total,
        "duration_sec": total_duration,
        "success_200": success_200,
        "busy_503": busy_503,
        "errors": errors,
        "latencies": latencies,
        "avg_latency_ms": avg_latency,
        "min_latency_ms": min_latency,
        "max_latency_ms": max_latency,
        "rejection_rate_pct": (busy_503 / total) * 100 if total else 0
    }


if __name__ == "__main__":
    run_dos_simulation()
