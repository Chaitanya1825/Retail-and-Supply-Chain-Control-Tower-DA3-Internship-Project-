"""
What-If Scenario Simulation Module for Retail & Supply Chain Control Tower.
Simulates a 7-day supplier delivery delay scenario.
Evaluates:
- How the delay impacts inventory availability
- Projected stockouts and unit shortages
- Severity classification across all products and suppliers
Stores results in PostgreSQL (what_if_scenarios table).
"""
import sys
from datetime import datetime
from pathlib import Path
import pandas as pd
import numpy as np

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from config.settings import get_engine, DELAY_SIMULATION_DAYS

def run_what_if_delay_scenario(added_delay_days: int = DELAY_SIMULATION_DAYS):
    """Simulates a supplier delay scenario across all products and suppliers."""
    engine = get_engine()
    print("=" * 60)
    print(f"  RUNNING WHAT-IF ANALYSIS: {added_delay_days}-DAY SUPPLIER DELIVERY DELAY")
    print("=" * 60)
    
    with engine.connect() as conn:
        df_products = pd.read_sql("SELECT * FROM products", conn)
        df_inventory = pd.read_sql("SELECT * FROM inventory", conn)
        df_product_kpis = pd.read_sql("SELECT * FROM product_kpis", conn)
        df_suppliers = pd.read_sql("SELECT supplier_id, supplier_name, reliability_score FROM suppliers", conn)
        
    merged = pd.merge(df_products, df_inventory[["product_id", "current_stock", "safety_stock"]], on="product_id", how="left")
    merged = pd.merge(merged, df_product_kpis[["product_id", "avg_daily_demand_30d"]], on="product_id", how="left")
    merged = pd.merge(merged, df_suppliers, on="supplier_id", how="left")
    
    scenario_records = []
    stockout_count = 0
    total_shortage_units = 0
    
    for _, row in merged.iterrows():
        p_id = row["product_id"]
        s_id = row["supplier_id"]
        p_name = row["product_name"]
        cat = row["category"]
        orig_lead = int(row["lead_time_days"])
        sim_lead = orig_lead + added_delay_days
        curr_stock = int(row["current_stock"])
        safety = int(row["safety_stock"])
        daily_demand = max(0.2, float(row["avg_daily_demand_30d"]))
        
        # Expected demand during the added delay period
        delay_demand = round(added_delay_days * daily_demand, 2)
        # Total demand during entire simulated lead time
        total_lead_demand = round(sim_lead * daily_demand, 2)
        
        projected_balance = curr_stock - total_lead_demand
        
        if projected_balance < 0:
            stockout_risk = True
            shortage_units = int(abs(projected_balance))
            stockout_count += 1
            total_shortage_units += shortage_units
            
            if shortage_units > 40 or curr_stock == 0:
                severity = "CRITICAL"
            elif shortage_units > 15:
                severity = "HIGH"
            else:
                severity = "MEDIUM"
        elif projected_balance <= safety:
            stockout_risk = False
            shortage_units = 0
            severity = "LOW"
        else:
            stockout_risk = False
            shortage_units = 0
            severity = "NONE"
            
        scenario_records.append({
            "scenario_name": f"{added_delay_days}_DAY_SUPPLIER_DELAY",
            "product_id": p_id,
            "supplier_id": s_id,
            "product_name": p_name,
            "category": cat,
            "original_lead_time_days": orig_lead,
            "simulated_lead_time_days": sim_lead,
            "current_inventory": curr_stock,
            "expected_demand_during_delay": delay_demand,
            "projected_stockout_risk": bool(stockout_risk),
            "estimated_units_shortage": shortage_units,
            "impact_severity": severity,
            "analyzed_at": datetime.now()
        })
        
    df_scenario = pd.DataFrame(scenario_records)
    
    print(f"[*] Evaluated 100 products under a {added_delay_days}-day supplier delay:")
    print(f"    -> Products facing projected stock-outs: {stockout_count} / 100 ({stockout_count}%)")
    print(f"    -> Estimated total unit shortage: {total_shortage_units:,} units")
    print(f"    -> Critical risk products: {(df_scenario['impact_severity'] == 'CRITICAL').sum()}")
    print(f"    -> High risk products: {(df_scenario['impact_severity'] == 'HIGH').sum()}")
    print(f"    -> Medium risk products: {(df_scenario['impact_severity'] == 'MEDIUM').sum()}")
    
    print("[*] Persisting What-If scenario results to PostgreSQL...")
    with engine.begin() as conn:
        conn.exec_driver_sql("TRUNCATE TABLE what_if_scenarios CASCADE;")
        df_scenario.to_sql("what_if_scenarios", conn, if_exists="append", index=False)
        
    print("[✓] What-if scenario analysis saved successfully.")
    print("=" * 60)
    return df_scenario

if __name__ == "__main__":
    run_what_if_delay_scenario()

