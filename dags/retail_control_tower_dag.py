"""
Apache Airflow DAG: Retail & Supply Chain Control Tower Hourly Pipeline.
Runs every hour to:
1. Refresh inventory and shipment states
2. Calculate supply chain KPIs (Stock-out rate, OTD %, Lead time, DOI)
3. Detect statistical Z-Score anomalies (Demand spikes & unexpected shipment delays)
4. Update Prophet 7-day demand forecasts & identify stockout risks
5. Run What-If 7-day supplier delay simulation
6. Dispatch critical exception alerts
"""
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# Add project root directory to sys.path so modules can be imported inside Airflow
DAG_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = DAG_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from airflow import DAG
    from airflow.operators.python import PythonOperator
    from airflow.utils.dates import days_ago
    AIRFLOW_AVAILABLE = True
except ImportError:
    AIRFLOW_AVAILABLE = False

from scripts.refresh_data import refresh_inventory_and_shipments
from scripts.calculate_kpis import calculate_and_store_kpis
from scripts.detect_anomalies import run_anomaly_detection
from scripts.forecast_demand import generate_demand_forecasts
from scripts.what_if_analysis import run_what_if_delay_scenario
from scripts.send_alerts import send_alert_notification

# Default DAG arguments
default_args = {
    "owner": "control_tower_analytics",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}

if AIRFLOW_AVAILABLE:
    with DAG(
        dag_id="retail_supply_chain_control_tower",
        default_args=default_args,
        description="Hourly Control Tower Pipeline: Ingestion, KPIs, Anomalies, Forecasts & Alerts",
        schedule_interval="0 * * * *",  # Hourly schedule
        start_date=days_ago(1),
        catchup=False,
        max_active_runs=1,
        tags=["retail", "supply_chain", "control_tower", "hourly", "prophet"],
    ) as dag:

        # Task 1: Refresh inventory and shipment states
        t1_refresh = PythonOperator(
            task_id="refresh_inventory_and_shipments",
            python_callable=refresh_inventory_and_shipments,
        )

        # Task 2: Calculate Control Tower KPIs
        t2_kpis = PythonOperator(
            task_id="calculate_kpis",
            python_callable=calculate_and_store_kpis,
        )

        # Task 3: Detect statistical Z-score anomalies
        t3_anomalies = PythonOperator(
            task_id="detect_anomalies",
            python_callable=run_anomaly_detection,
        )

        # Task 4: Run Prophet 7-day demand forecasts
        t4_forecasts = PythonOperator(
            task_id="update_demand_forecasts",
            python_callable=generate_demand_forecasts,
        )

        # Task 5: Simulate What-If 7-Day Supplier Delay
        t5_what_if = PythonOperator(
            task_id="run_what_if_analysis",
            python_callable=run_what_if_delay_scenario,
        )

        # Task 6: Send automated alert notifications
        t6_alerts = PythonOperator(
            task_id="send_alerts",
            python_callable=send_alert_notification,
        )

        # Define DAG Execution Flow
        t1_refresh >> [t2_kpis, t3_anomalies, t4_forecasts] >> t5_what_if >> t6_alerts

