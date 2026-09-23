# Security Lab Assignment: Controlled DoS & DDoS Simulation

**GitHub Repository**: [https://github.com/jim2107054/security_assignment](https://github.com/jim2107054/security_assignment)

## Folder Structure
- `code/`: Contains all simulation source code and dependencies.
  - `requirements.txt`: Python package requirements.
  - `server.py`: Dummy Flask server on `127.0.0.1:5000`.
  - `baseline.py`: Normal traffic baseline measurement.
  - `client.py`: Controlled single-source DoS traffic simulation.
  - `ddos_sim.py`: Controlled multi-process DDoS traffic simulation.
- `report/`: Contains the report.
  - `report.pdf`: Compiled academic report PDF.
  - `report.tex`: Academic LaTeX source.

## How to Run
1. Open a terminal and navigate to `code/`:
   ```bash
   cd code
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Start the target server:
   ```bash
   python server.py
   ```
4. In another terminal, run the tests:
   ```bash
   cd code
   python baseline.py
   python client.py
   python ddos_sim.py
   ```
