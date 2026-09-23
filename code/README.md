# Controlled DoS & DDoS Simulation - Code Runner Guide

This directory contains the complete, self-contained Python source code for the security laboratory assignment.

## Prerequisites
- Python 3 (Python 3.8 or higher)
- pip

## Quickstart (Cross-Platform: Windows, macOS, Linux)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Target Web Server
```bash
python server.py
```
*The server will start on `http://127.0.0.1:5000/`. You can open this URL in any browser to see the interactive interface.*

### 3. Run the Experiments (in a separate terminal)

- **Stage A: Normal Baseline Measurement**
  ```bash
  python baseline.py
  ```

- **Stage B: Single-Source DoS Simulation**
  ```bash
  python client.py
  ```

- **Stage C: Multi-Process DDoS Botnet Simulation**
  ```bash
  python ddos_sim.py
  ```
