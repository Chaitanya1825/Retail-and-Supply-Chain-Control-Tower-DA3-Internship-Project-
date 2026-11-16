"""
Unified Pipeline Orchestrator for Retail & Supply Chain Control Tower.
Executes the hourly workflow locally or in scheduled mode.
Mirrors the exact Airflow DAG execution flow without requiring Docker.
"""
import sys
import time
import argparse
from datetime import datetime
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.refresh_data import refresh_inventory_and_shipments
from scripts.calculate_kpis import calculate_and_store_kpis
from scripts.detect_anomalies import run_anomaly_detection
from scripts.forecast_demand import generate_demand_forecasts
from scripts.what_if_analysis import run_what_if_delay_scenario
from scripts.send_alerts import send_alert_notification

def execute_pipeline(horizon_days: int = 7, delay_days: int = 7):
    """Executes all pipeline tasks in sequence with error handling and timing metrics."""
    pipeline_start = datetime.now()
    print("\n" + "#" * 65)
    print(f"  STARTING RETAIL & SUPPLY CHAIN CONTROL TOWER PIPELINE")
    print(f"  Execution Time: {pipeline_start.strftime('%Y-%m-%d %H:%M:%S')}")
    print("#" * 65 + "\n")
    
    stages = [
        ("Task 1: Refresh Inventory & Shipments", lambda: refresh_inventory_and_shipments()),
        ("Task 2: Calculate Supply Chain KPIs", lambda: calculate_and_store_kpis()),
        ("Task 3: Run Z-Score Anomaly Detection", lambda: run_anomaly_detection()),
        ("Task 4: Update Prophet Demand Forecasts", lambda: generate_demand_forecasts(horizon_days=horizon_days)),
        ("Task 5: Execute What-If Delay Analysis", lambda: run_what_if_delay_scenario(added_delay_days=delay_days)),
        ("Task 6: Check Conditions & Dispatch Alerts", lambda: send_alert_notification()),
    ]
    
    for stage_name, stage_fn in stages:
        stage_start = time.time()
        print(f"\n>>> Running {stage_name}...")
        try:
            stage_fn()
            elapsed = time.time() - stage_start
            print(f"[✓] Completed {stage_name} in {elapsed:.2f}s")
        except Exception as e:
            print(f"[!] ERROR in {stage_name}: {e}")
            raise
            
    total_elapsed = (datetime.now() - pipeline_start).total_seconds()
    print("\n" + "=" * 65)
    print(f"  PIPELINE EXECUTION COMPLETED SUCCESSFULLY IN {total_elapsed:.2f}s")
    print("=" * 65 + "\n")

def main():
    parser = argparse.ArgumentParser(description="Control Tower Pipeline Runner")
    parser.add_argument("--loop", action="store_true", help="Run continuously on an hourly interval")
    parser.add_argument("--interval", type=int, default=3600, help="Interval in seconds for loop mode (default: 3600)")
    parser.add_argument("--horizon", type=int, default=7, help="Prophet forecast horizon in days (default: 7)")
    parser.add_argument("--delay-days", type=int, default=7, help="What-if simulated delay in days (default: 7)")
    args = parser.parse_args()
    
    if args.loop:
        print(f"[*] Starting Control Tower daemon (running every {args.interval} seconds)...")
        while True:
            try:
                execute_pipeline(horizon_days=args.horizon, delay_days=args.delay_days)
            except Exception as err:
                print(f"[!] Pipeline iteration error: {err}")
            print(f"[*] Sleeping for {args.interval} seconds until next hourly run...")
            time.sleep(args.interval)
    else:
        execute_pipeline(horizon_days=args.horizon, delay_days=args.delay_days)

if __name__ == "__main__":
    main()

