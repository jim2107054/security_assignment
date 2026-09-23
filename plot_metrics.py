"""
Controlled DoS & DDoS Simulation Lab - Metrics Plotting Tool
File: plot_metrics.py
Description: Generates publication-quality charts from 'experiment_results.json'
             for the formal academic security lab report.
"""

import json
import os
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker


def generate_plots(json_file="experiment_results.json"):
    if not os.path.exists(json_file):
        print(f"[!] Error: {json_file} not found. Please run experiment_orchestrator.py first.")
        return

    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    stages = ["Baseline", "DoS Attack", "DDoS Cluster", "Recovery"]
    stage_keys = ["baseline", "dos", "ddos", "recovery"]

    success_counts = [data[k]["success_200"] for k in stage_keys]
    busy_counts = [data[k]["busy_503"] for k in stage_keys]
    total_counts = [data[k]["total"] for k in stage_keys]
    avg_latencies = [data[k]["avg_latency_ms"] for k in stage_keys]

    # Set dark-themed / modern styling for charts
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5), dpi=300)

    # -------------------------------------------------------------
    # Plot 1: HTTP Status Distribution (200 OK vs 503 Service Unavailable)
    # -------------------------------------------------------------
    x = range(len(stages))
    bar_width = 0.35

    rects1 = ax1.bar([i - bar_width/2 for i in x], success_counts, bar_width, label='HTTP 200 (Success)', color='#22c55e', edgecolor='#15803d', alpha=0.9)
    rects2 = ax1.bar([i + bar_width/2 for i in x], busy_counts, bar_width, label='HTTP 503 (Capacity Rejection)', color='#ef4444', edgecolor='#b91c1c', alpha=0.9)

    ax1.set_ylabel('Number of Requests', fontsize=11, fontweight='bold')
    ax1.set_title('Request Processing Distribution by Attack Stage', fontsize=12, fontweight='bold', pad=12)
    ax1.set_xticks(list(x))
    ax1.set_xticklabels(stages, fontsize=10, fontweight='medium')
    ax1.legend(loc='upper right', frameon=True)
    ax1.grid(axis='y', linestyle='--', alpha=0.7)

    # Add count labels on bars
    for rect in rects1:
        h = rect.get_height()
        if h > 0:
            ax1.annotate(f'{int(h)}', xy=(rect.get_x() + rect.get_width() / 2, h),
                         xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=9, fontweight='bold')
    for rect in rects2:
        h = rect.get_height()
        if h > 0:
            ax1.annotate(f'{int(h)}', xy=(rect.get_x() + rect.get_width() / 2, h),
                         xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=9, fontweight='bold', color='#b91c1c')

    # -------------------------------------------------------------
    # Plot 2: Average Latency Across Stages (ms)
    # -------------------------------------------------------------
    bars = ax2.bar(stages, avg_latencies, color=['#3b82f6', '#f59e0b', '#dc2626', '#10b981'], edgecolor='#1e293b', width=0.5, alpha=0.85)
    ax2.set_ylabel('Mean Latency (ms)', fontsize=11, fontweight='bold')
    ax2.set_title('Mean Request Latency Across Experimental Stages', fontsize=12, fontweight='bold', pad=12)
    ax2.grid(axis='y', linestyle='--', alpha=0.7)

    for bar in bars:
        h = bar.get_height()
        ax2.annotate(f'{h:.1f} ms', xy=(bar.get_x() + bar.get_width() / 2, h),
                     xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=9, fontweight='bold')

    plt.tight_layout()
    output_chart = "experimental_metrics_plot.png"
    plt.savefig(output_chart, bbox_inches='tight')
    plt.close()
    print(f"[+] Comparison graph generated: {output_chart}")


if __name__ == "__main__":
    generate_plots()
