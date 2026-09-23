# Controlled DoS & DDoS Simulation Lab Project

This repository contains the complete implementation and academic report for the **Controlled DoS & DDoS Simulation on a Local Dummy Web Server** security assignment.

---

## 📁 Project Structure & Renamed Files

| Original Template Name | Renamed Project File | Description |
| :--- | :--- | :--- |
| `server.py` | [app_target_server.py](file:///y:/4-1/Computer%20Security/security_assignment/app_target_server.py) | Dummy Flask target server (`CAPACITY=4`, `PROCESSING_TIME=0.25s`, endpoints: `/`, `/work`, `/stats`, `/reset`) |
| `baseline.py` | [baseline_evaluator.py](file:///y:/4-1/Computer%20Security/security_assignment/baseline_evaluator.py) | Measures baseline latency & 100% success rate under normal traffic (Stage A) |
| `client.py` | [dos_traffic_generator.py](file:///y:/4-1/Computer%20Security/security_assignment/dos_traffic_generator.py) | Single-source concurrent DoS attack simulation (Stage B) |
| `ddos_sim.py` | [ddos_cluster_simulator.py](file:///y:/4-1/Computer%20Security/security_assignment/ddos_cluster_simulator.py) | Multi-process distributed DDoS cluster simulation (Stage C) |
| *(New)* | [experiment_orchestrator.py](file:///y:/4-1/Computer%20Security/security_assignment/experiment_orchestrator.py) | End-to-end benchmark coordinator that runs Stages A--D and exports data |
| *(New)* | [plot_metrics.py](file:///y:/4-1/Computer%20Security/security_assignment/plot_metrics.py) | Generates high-resolution publication charts (`experimental_metrics_plot.png`) |
| `report.tex` | [security_lab_report.tex](file:///y:/4-1/Computer%20Security/security_assignment/security_lab_report.tex) | Full Academic LaTeX Lab Report (IEEE/ACM style with TikZ topology & tables) |
| `REPORT.md` | [LAB_REPORT.md](file:///y:/4-1/Computer%20Security/security_assignment/LAB_REPORT.md) | Complete Markdown lab report for instant preview in IDE |

---

## 🚀 Quickstart: How to Run the Experiment

### 1. Activate Environment & Dependencies
```bash
# Windows PowerShell
.venv\Scripts\activate
```

### 2. Start the Target Web Server
Open a terminal and run:
```bash
python app_target_server.py
```
Server will be listening at `http://127.0.0.1:5000/`.

### 3. Run the Automated Experiment Suite
In a second terminal:
```bash
python experiment_orchestrator.py
```
This automatically runs:
- **Stage A (Baseline):** 20 requests with 150ms delay $\to$ 100% 200 OK
- **Stage B (DoS Simulation):** 80 concurrent requests $\to$ ~92.5% HTTP 503 Busy
- **Stage C (DDoS Simulation):** 4 multi-process workers (100 concurrent requests) $\to$ ~92.0% HTTP 503 Busy
- **Stage D (Recovery):** 15 sequential probe requests $\to$ 100% 200 OK (Full recovery)
- Saves all measurements to `experiment_results.json`.

### 4. Generate Visual Charts
```bash
python plot_metrics.py
```
Creates `experimental_metrics_plot.png`.

---

## 📄 How to Compile the LaTeX Report (`security_lab_report.tex`)

### Option 1: Overleaf (Recommended - No Installation Required)
1. Go to **[Overleaf](https://www.overleaf.com/)** and log in.
2. Click **New Project** $\to$ **Blank Project**.
3. Copy and paste the entire code from [security_lab_report.tex](file:///y:/4-1/Computer%20Security/security_assignment/security_lab_report.tex) into `main.tex`.
4. Upload `experimental_metrics_plot.png` into the project root on Overleaf.
5. Click **Recompile** to generate and download the high-quality PDF report!

### Option 2: Local Compilation (if MiKTeX / TeX Live is installed)
```bash
pdflatex security_lab_report.tex
```
