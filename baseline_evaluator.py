"""
Controlled DoS & DDoS Simulation Lab - Baseline Evaluator
File: baseline_evaluator.py
Description: Measures baseline server performance under normal, low-rate traffic.
             Sends 20 sequential requests and evaluates baseline latency and reliability.
"""

import time
import requests

TARGET_URL = "http://127.0.0.1:5000/work"
TOTAL_REQUESTS = 20
REQUEST_DELAY = 0.15  # 150ms delay between consecutive requests


def run_baseline_test(url=TARGET_URL, total=TOTAL_REQUESTS, delay=REQUEST_DELAY):
    print("=" * 60)
    print(" [STAGE A: BASELINE MEASUREMENT]")
    print(f" Target URL: {url}")
    print(f" Request Count: {total} | Inter-request Delay: {delay}s")
    print("=" * 60)

    latencies = []
    success_count = 0
    failed_count = 0

    for i in range(total):
        start_time = time.perf_counter()
        try:
            response = requests.get(url, timeout=3)
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            latencies.append(elapsed_ms)

            if response.status_code == 200:
                success_count += 1
                status_str = f"HTTP {response.status_code} [OK]"
            else:
                failed_count += 1
                status_str = f"HTTP {response.status_code} [BUSY/ERR]"

            print(f" Request [{i+1:02d}/{total:02d}]: {status_str} in {elapsed_ms:.2f} ms")
        except requests.RequestException as exc:
            failed_count += 1
            print(f" Request [{i+1:02d}/{total:02d}]: CONNECTION ERROR -> {exc}")

        time.sleep(delay)

    avg_latency = (sum(latencies) / len(latencies)) if latencies else 0.0
    min_latency = min(latencies) if latencies else 0.0
    max_latency = max(latencies) if latencies else 0.0

    print("\n" + "-" * 30 + " BASELINE SUMMARY " + "-" * 30)
    print(f" Total Requests Transmitted : {total}")
    print(f" Successful Requests (200)   : {success_count} ({success_count/total*100:.1f}%)")
    print(f" Failed/Rejected (503/other): {failed_count} ({failed_count/total*100:.1f}%)")
    print(f" Average Latency            : {avg_latency:.2f} ms")
    print(f" Latency Range (Min / Max)  : {min_latency:.2f} ms / {max_latency:.2f} ms")
    print("-" * 78)

    return {
        "stage": "Baseline",
        "total": total,
        "success_200": success_count,
        "busy_503": 0,
        "errors": failed_count,
        "latencies": latencies,
        "avg_latency_ms": avg_latency,
        "min_latency_ms": min_latency,
        "max_latency_ms": max_latency,
        "success_rate_pct": (success_count / total) * 100 if total else 0
    }


if __name__ == "__main__":
    run_baseline_test()
