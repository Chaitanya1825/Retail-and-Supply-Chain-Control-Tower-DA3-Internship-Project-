# 💻 Windows PowerShell Execution & Administration Guide

This guide provides simple, copy-pasteable PowerShell commands to set up, initialize, run, test, and manage the **Retail & Supply Chain Control Tower** on Windows.

---

## 1. Environment Setup

### 1.1 Open PowerShell in Project Directory
Launch Windows PowerShell and navigate to the repository directory:
```powershell
cd "c:\Users\HP\Desktop\Retail and Supply Chain Control Tower"
```

### 1.2 Create and Activate Python Virtual Environment (Recommended)
```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1
```
*(If script execution is blocked on your system, run: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`)*

### 1.3 Install Required Dependencies
```powershell
pip install -r requirements.txt
```

### 1.4 Configure Environment File
Copy the example configuration to `.env` and verify your local PostgreSQL credentials:
```powershell
Copy-Item .env.example .env
```
Ensure `.env` matches your local setup:
```ini
DB_HOST=localhost
DB_PORT=5432
DB_NAME=supply_chain_control_tower
DB_USER=postgres
DB_PASSWORD=YourLocalPostgresPassword
```

---

## 2. All-in-One Execution (Fast Track)

### 2.1 Interactive Terminal Menu
For convenience, launch the interactive PowerShell quick-menu:
```powershell
.\run.ps1
```

### 2.2 Run Full Pipeline End-to-End
Execute database initialization, data generation, KPI calculation, anomaly detection, Prophet forecasting, what-if analysis, and alerting in a single command:
```powershell
# Initialize DB & generate synthetic data (First run)
python scripts\init_db.py
python scripts\generate_data.py

# Run all analytics models & forecasting
python run_pipeline.py
```

### 2.3 Launch the Control Tower Dashboard
Start the interactive SaaS web dashboard:
```powershell
streamlit run run_dashboard.py
```
Open your browser to: **`http://localhost:8501`**.

---

## 3. Step-by-Step Modular Pipeline Execution

Each stage of the Control Tower can be run individually for debugging or modular scheduling:

### Stage 1: Database Initialization
Creates the PostgreSQL database `supply_chain_control_tower`, 11 relational tables, and 6 analytical views:
```powershell
python scripts\init_db.py
```

### Stage 2: Generate Realistic Synthetic Data
Synthesizes 10 suppliers, 100 products, inventory records, 90 days of sales transactions (3,600+ orders), and purchase order shipments:
```powershell
python scripts\generate_data.py
```

### Stage 3: Hourly Inventory & Shipment Refresh
Simulates hourly stock burn and updates in-transit supplier deliveries:
```powershell
python scripts\refresh_data.py
```

### Stage 4: Calculate Supply Chain KPIs
Calculates Stock-out rate, On-Time Delivery percentage (OTD %), Average Lead Time, and Days of Inventory (DOI):
```powershell
python scripts\calculate_kpis.py
```

### Stage 5: Z-Score Statistical Anomaly Detection
Identifies demand surges and logistics transit delays exceeding $|Z| \ge 2.0$:
```powershell
python scripts\detect_anomalies.py
```

### Stage 6: Facebook Prophet Demand Forecasting
Fits time-series models across all 100 SKUs to generate 700 daily forecast points and evaluate stockout risk:
```powershell
python scripts\forecast_demand.py
```

### Stage 7: What-If 7-Day Delay Scenario Simulation
Simulates an unexpected +7-day supplier delay and calculates inventory shortages across all SKUs:
```powershell
python scripts\what_if_analysis.py
```

### Stage 8: Operational Alerts & Exception Notifications
Scans for critical stockouts and high-severity delays, logging events to `alert_logs` and sending email digests (if SMTP configured):
```powershell
python scripts\send_alerts.py
```

---

## 4. Continuous Daemon Execution (Hourly Loop)

To run the pipeline continuously in the background on Windows without needing Apache Airflow or Docker:
```powershell
# Runs pipeline every hour (3600 seconds)
python run_pipeline.py --loop --interval 3600
```

---

## 5. Automated Pipeline Testing & Verification

Run the automated test suite containing 27 validation checks across tables, analytical views, formulas, and forecasting logic:
```powershell
python scripts\test_pipeline.py
```
Expected output:
```
=================================================================
  TEST RESULTS: 27/27 CHECKS PASSED (100.0%)
=================================================================
```

---

## 6. Docker Services (Apache Airflow & Apache Superset)

Run optional enterprise services using isolated Docker Compose profiles:

### 6.1 Run Apache Airflow Only
```powershell
docker compose --profile airflow up -d
```
- Airflow Web UI: `http://localhost:8080` (Username: `admin`, Password: `admin`)
- DAG: `retail_control_tower_pipeline` (Hourly schedule: `0 * * * *`)

### 6.2 Run Apache Superset Only
```powershell
docker compose --profile superset up -d
```
- Superset Web UI: `http://localhost:8088` (Username: `admin`, Password: `admin`)
- Import dashboard assets from `docs/superset/control_tower_dashboard_export.json`

### 6.3 Run Both Services
```powershell
docker compose --profile all up -d
```

### 6.4 Stop Docker Services
```powershell
docker compose --profile all down
```
