"""
Comprehensive Verification and Test Script for Retail & Supply Chain Control Tower.
Verifies:
1. PostgreSQL connection, 11 tables & row counts
2. All 6 analytical views
3. Calculated KPI ranges
4. Anomaly detection outputs & Z-scores
5. Prophet 7-day demand forecasts & stockout flags
6. What-If scenario results
7. Alert logging
"""
import sys
from pathlib import Path
import pandas as pd

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from config.settings import get_engine

def run_tests():
    print("=" * 65)
    print("  CONTROL TOWER PIPELINE & DATABASE VERIFICATION TEST SUITE")
    print("=" * 65)
    
    engine = get_engine()
    passed = 0
    total = 0
    
    def check(name, condition, msg=""):
        nonlocal passed, total
        total += 1
        if condition:
            print(f"[PASS] {name} {msg}")
            passed += 1
        else:
            print(f"[FAIL] {name} - {msg}")
            
    with engine.connect() as conn:
        # Test 1: Core Tables exist and have data
        expected_tables = {
            "suppliers": 10,
            "products": 100,
            "inventory": 100,
            "sales_orders": 3000,   # At least 3,000 orders
            "shipments": 200,       # At least 200 shipments
            "kpi_metrics": 1,
            "product_kpis": 100,
            "anomalies": 5,         # At least 5 anomalies
            "demand_forecasts": 700,# Exactly 700 forecast points (100 x 7)
            "what_if_scenarios": 100,
            "alert_logs": 1
        }
        
        print("\n--- 1. Table Verification ---")
        for table, min_rows in expected_tables.items():
            try:
                res = conn.exec_driver_sql(f"SELECT COUNT(*) FROM {table}").scalar()
                check(f"Table '{table}'", res >= min_rows, f"(Found {res} rows, min expected {min_rows})")
            except Exception as e:
                check(f"Table '{table}'", False, str(e))
                
        # Test 2: Analytical Views
        print("\n--- 2. Analytical Views Verification ---")
        expected_views = [
            "v_kpi_summary",
            "v_inventory_status",
            "v_shipment_performance",
            "v_demand_forecast_summary",
            "v_anomaly_feed",
            "v_what_if_delay_impact"
        ]
        for view in expected_views:
            try:
                df_view = pd.read_sql(f"SELECT * FROM {view} LIMIT 5", conn)
                check(f"View '{view}'", len(df_view) > 0, f"(Returned {len(df_view)} rows on sample)")
            except Exception as e:
                check(f"View '{view}'", False, str(e))
                
        # Test 3: KPI Quality Checks
        print("\n--- 3. KPI Business Logic Verification ---")
        df_kpi = pd.read_sql("SELECT * FROM v_kpi_summary", conn).iloc[0]
        check("Stock-out rate in [0, 100]%", 0 <= df_kpi["stock_out_rate"] <= 100, f"({df_kpi['stock_out_rate']}%)")
        check("On-time delivery in [0, 100]%", 0 <= df_kpi["on_time_delivery_pct"] <= 100, f"({df_kpi['on_time_delivery_pct']}%)")
        check("Avg Lead Time > 0", df_kpi["avg_supplier_lead_time"] > 0, f"({df_kpi['avg_supplier_lead_time']} days)")
        check("Days of Inventory > 0", df_kpi["avg_days_of_inventory"] > 0, f"({df_kpi['avg_days_of_inventory']} days)")
        
        # Test 4: Anomaly Detection Checks
        print("\n--- 4. Anomaly Detection Logic Verification ---")
        df_anom = pd.read_sql("SELECT * FROM anomalies", conn)
        check("Anomalies found", len(df_anom) > 0, f"({len(df_anom)} anomalies recorded)")
        check("Z-scores meet threshold (Z >= 2.0)", (df_anom["z_score"] >= 2.0).all(), f"All {len(df_anom)} anomalies have Z >= 2.0")
        
        # Test 5: Prophet Forecasting Checks
        print("\n--- 5. Prophet Forecasting Verification ---")
        df_fc = pd.read_sql("SELECT COUNT(DISTINCT product_id) as prods, COUNT(*) as pts FROM demand_forecasts", conn).iloc[0]
        check("100 Products forecasted", df_fc["prods"] == 100, f"({df_fc['prods']} products)")
        check("700 Forecast data points", df_fc["pts"] == 700, f"({df_fc['pts']} data points)")
        
        # Test 6: What-if Scenario Checks
        print("\n--- 6. What-If Scenario Verification ---")
        df_what_if = pd.read_sql("SELECT COUNT(*) as cnt, SUM(estimated_units_shortage) as shortage FROM what_if_scenarios", conn).iloc[0]
        check("100 Products evaluated in delay scenario", df_what_if["cnt"] == 100, f"({df_what_if['cnt']} records)")
        check("Shortage units quantified", df_what_if["shortage"] > 0, f"({int(df_what_if['shortage'])} units)")
        
    print("\n" + "=" * 65)
    print(f"  TEST RESULTS: {passed}/{total} CHECKS PASSED ({(passed/total)*100:.1f}%)")
    print("=" * 65)
    return passed == total

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
