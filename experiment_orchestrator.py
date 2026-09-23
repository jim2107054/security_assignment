"""
Controlled DoS & DDoS Simulation Lab - Experiment Orchestrator
File: experiment_orchestrator.py
Description: End-to-end automated experiment runner that coordinates all 4 stages:
             Stage A: Baseline evaluation (low rate)
             Stage B: Single-generator DoS attack
             Stage C: Multi-worker DDoS attack
             Stage D: Post-attack recovery verification
             Collects and saves all experimental measurements into 'experiment_results.json'.
"""

import json
import time
import requests

from baseline_evaluator import run_baseline_test
from dos_traffic_generator import run_dos_simulation
from ddos_cluster_simulator import run_ddos_simulation

SERVER_BASE_URL = "http://127.0.0.1:5000"
WORK_URL = f"{SERVER_BASE_URL}/work"
STATS_URL = f"{SERVER_BASE_URL}/stats"
RESET_URL = f"{SERVER_BASE_URL}/reset"


def verify_server_online():
    """Checks if dummy target server is running."""
    try:
        r = requests.get(SERVER_BASE_URL, timeout=3)
        return r.status_code == 200
    except requests.RequestException:
        return False


def reset_server_counters():
    """Resets server statistics."""
    try:
        requests.get(RESET_URL, timeout=2)
    except Exception:
        pass


def fetch_server_stats():
    """Retrieves current server counters."""
    try:
        r = requests.get(STATS_URL, timeout=2)
        return r.json()
    except Exception:
        return {"accepted": 0, "rejected": 0}


def run_recovery_test(count=15, delay=0.15):
    """
    Stage D: Recovery Verification
    Tests if server returns to 100% availability after attack traffic ceases.
    """
    print("=" * 60)
    print(" [STAGE D: SERVICE RECOVERY VERIFICATION]")
    print(f" Probing server with {count} legitimate sequential requests...")
    print("=" * 60)

    success = 0
    failed = 0
    latencies = []

    for i in range(count):
        t0 = time.perf_counter()
        try:
            r = requests.get(WORK_URL, timeout=3.0)
            elapsed = (time.perf_counter() - t0) * 1000
            latencies.append(elapsed)
            if r.status_code == 200:
                success += 1
                status = "HTTP 200 [OK]"
            else:
                failed += 1
                status = f"HTTP {r.status_code} [BUSY]"
            print(f" Recovery Probe #{i+1:02d}: {status} ({elapsed:.2f} ms)")
        except requests.RequestException as e:
            failed += 1
            print(f" Recovery Probe #{i+1:02d}: ERROR -> {e}")

        time.sleep(delay)

    avg_lat = (sum(latencies) / len(latencies)) if latencies else 0.0
    print("\n" + "-" * 30 + " RECOVERY SUMMARY " + "-" * 30)
    print(f" Recovery Requests  : {count}")
    print(f" Success (HTTP 200) : {success} ({success/count*100:.1f}%)")
    print(f" Failed/Rejected    : {failed}")
    print(f" Avg Latency        : {avg_lat:.2f} ms")
    print("-" * 78)

    return {
        "stage": "Recovery",
        "total": count,
        "success_200": success,
        "busy_503": failed,
        "errors": 0,
        "latencies": latencies,
        "avg_latency_ms": avg_lat,
        "min_latency_ms": min(latencies) if latencies else 0,
        "max_latency_ms": max(latencies) if latencies else 0,
        "recovery_rate_pct": (success / count) * 100 if count else 0
    }


def main():
    print("*" * 65)
    print("   CONTROLLED APPLICATION-LAYER DoS & DDoS LAB SUITE   ")
    print("*" * 65)

    if not verify_server_online():
        print("\n[!] ERROR: Target server is not running on http://127.0.0.1:5000.")
        print("    Please start 'app_target_server.py' in a separate terminal before running this suite.")
        return

    print("\n[+] Target Server confirmed ONLINE. Initializing benchmarks...\n")

    full_results = {}

    # 1. STAGE A: BASELINE
    reset_server_counters()
    time.sleep(0.5)
    stage_a = run_baseline_test(url=WORK_URL, total=20, delay=0.15)
    stage_a["server_stats"] = fetch_server_stats()
    full_results["baseline"] = stage_a
    time.sleep(1.0)

    # 2. STAGE B: DoS SIMULATION
    reset_server_counters()
    time.sleep(0.5)
    stage_b = run_dos_simulation(url=WORK_URL, total=80, threads=8)
    stage_b["server_stats"] = fetch_server_stats()
    full_results["dos"] = stage_b
    time.sleep(1.0)

    # 3. STAGE C: DDoS SIMULATION
    reset_server_counters()
    time.sleep(0.5)
    stage_c = run_ddos_simulation(url=WORK_URL, workers=4, req_per_worker=25, threads=4)
    stage_c["server_stats"] = fetch_server_stats()
    full_results["ddos"] = stage_c
    time.sleep(1.0)

    # 4. STAGE D: RECOVERY VERIFICATION
    reset_server_counters()
    time.sleep(0.5)
    stage_d = run_recovery_test(count=15, delay=0.15)
    stage_d["server_stats"] = fetch_server_stats()
    full_results["recovery"] = stage_d

    # Export results
    output_filename = "experiment_results.json"
    with open(output_filename, "w", encoding="utf-8") as f:
        json.dump(full_results, f, indent=4)

    print("\n" + "=" * 65)
    print(f" [SUCCESS] All 4 experimental stages completed successfully!")
    print(f" [OUTPUT] Detailed numerical results saved to '{output_filename}'")
    print("=" * 65)


if __name__ == "__main__":
    main()
