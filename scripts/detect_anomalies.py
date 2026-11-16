"""
Anomaly Detection Module for Retail & Supply Chain Control Tower.
Implements Z-Score detection for:
1. Unusual Demand Spikes (Daily product order volumes)
2. Unexpected Shipment Delays (Supplier shipment delays & lead times)
Stores detected anomalies in PostgreSQL.
"""
import sys
from datetime import datetime
from pathlib import Path
import pandas as pd
import numpy as np
from scipy import stats

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from config.settings import get_engine, Z_SCORE_THRESHOLD

def detect_demand_spikes(conn, threshold: float = Z_SCORE_THRESHOLD) -> pd.DataFrame:
    """Calculates daily demand per product and identifies Z-Score spikes."""
    print("[*] Detecting Unusual Demand Spikes across products...")
    
    # Aggregate daily sales per product
    query = """
    SELECT 
        s.order_date,
        s.product_id,
        p.product_name,
        p.category,
        SUM(s.quantity_ordered) as daily_units,
        COUNT(s.order_id) as order_count
    FROM sales_orders s
    JOIN products p ON s.product_id = p.product_id
    GROUP BY s.order_date, s.product_id, p.product_name, p.category
    ORDER BY s.product_id, s.order_date;
    """
    df = pd.read_sql(query, conn)
    if df.empty:
        return pd.DataFrame()
        
    anomalies = []
    
    # Calculate Z-score per product across its 90-day time series
    for prod_id, group in df.groupby("product_id"):
        units = group["daily_units"].values
        mean_val = float(np.mean(units))
        std_val = float(np.std(units))
        
        # If std is zero or very small, skip
        if std_val < 0.1:
            continue
            
        z_scores = (units - mean_val) / std_val
        
        for idx, z in enumerate(z_scores):
            # Only positive spikes (demand surge)
            if z >= threshold:
                row = group.iloc[idx]
                severity = "CRITICAL" if z >= 3.0 else "HIGH"
                anomalies.append({
                    "anomaly_type": "DEMAND_SPIKE",
                    "reference_id": f"{row['product_id']}:{row['order_date']}",
                    "entity_name": f"{row['product_name']} ({row['category']})",
                    "metric_value": round(float(row["daily_units"]), 2),
                    "baseline_mean": round(mean_val, 2),
                    "baseline_std": round(std_val, 2),
                    "z_score": round(float(z), 2),
                    "severity": severity,
                    "details": f"Unusual surge of {int(row['daily_units'])} units ordered on {row['order_date']} (Normal baseline: {mean_val:.1f} ± {std_val:.1f} units).",
                    "detected_at": datetime.now(),
                    "status": "OPEN"
                })
                
    result_df = pd.DataFrame(anomalies)
    print(f"[✓] Detected {len(result_df)} Demand Spike anomalies.")
    return result_df

def detect_shipment_delays(conn, threshold: float = Z_SCORE_THRESHOLD) -> pd.DataFrame:
    """Identifies unexpected shipment delays and supplier lead-time anomalies using Z-scores."""
    print("[*] Detecting Unexpected Shipment Delays across suppliers...")
    
    query = """
    SELECT 
        sh.shipment_id,
        sh.supplier_id,
        s.supplier_name,
        sh.product_id,
        p.product_name,
        sh.order_date,
        sh.expected_delivery_date,
        sh.actual_delivery_date,
        sh.shipping_status,
        sh.lead_time_days,
        sh.delay_days,
        sh.is_delayed
    FROM shipments sh
    JOIN suppliers s ON sh.supplier_id = s.supplier_id
    JOIN products p ON sh.product_id = p.product_id
    WHERE sh.shipping_status IN ('DELIVERED', 'DELAYED');
    """
    df = pd.read_sql(query, conn)
    if df.empty:
        return pd.DataFrame()
        
    lead_times = df["lead_time_days"].dropna().values
    mean_lead = float(np.mean(lead_times))
    std_lead = float(np.std(lead_times))
    
    anomalies = []
    
    if std_lead > 0:
        z_scores = (df["lead_time_days"] - mean_lead) / std_lead
        df["z_score"] = z_scores
        
        # Delayed shipments exceeding z-score threshold
        outliers = df[(df["is_delayed"] == True) & (df["z_score"] >= threshold)]
        
        for _, row in outliers.iterrows():
            z = float(row["z_score"])
            severity = "CRITICAL" if (z >= 3.0 or row["delay_days"] >= 7) else "HIGH"
            anomalies.append({
                "anomaly_type": "SHIPMENT_DELAY",
                "reference_id": str(row["shipment_id"]),
                "entity_name": f"{row['supplier_name']} -> {row['product_name']}",
                "metric_value": round(float(row["lead_time_days"]), 2),
                "baseline_mean": round(mean_lead, 2),
                "baseline_std": round(std_lead, 2),
                "z_score": round(z, 2),
                "severity": severity,
                "details": f"Shipment {row['shipment_id']} delayed by {int(row['delay_days'])} days (Total lead time: {int(row['lead_time_days'])} days vs avg {mean_lead:.1f} days).",
                "detected_at": datetime.now(),
                "status": "OPEN"
            })
            
    result_df = pd.DataFrame(anomalies)
    print(f"[✓] Detected {len(result_df)} Unexpected Shipment Delay anomalies.")
    return result_df

def run_anomaly_detection():
    """Runs complete Z-score anomaly detection and stores findings in PostgreSQL."""
    engine = get_engine()
    print("=" * 60)
    print("  RUNNING STATISTICAL Z-SCORE ANOMALY DETECTION")
    print("=" * 60)
    
    with engine.connect() as conn:
        df_spikes = detect_demand_spikes(conn)
        df_delays = detect_shipment_delays(conn)
        
    combined_anomalies = pd.concat([df_spikes, df_delays], ignore_index=True)
    
    if not combined_anomalies.empty:
        print(f"[*] Storing {len(combined_anomalies)} total anomalies in database...")
        with engine.begin() as conn:
            conn.exec_driver_sql("TRUNCATE TABLE anomalies CASCADE;")
            combined_anomalies.to_sql("anomalies", conn, if_exists="append", index=False)
        print("[✓] Anomalies persisted successfully.")
    else:
        print("[*] No anomalies exceeding threshold found.")
        
    print("=" * 60)
    return combined_anomalies

if __name__ == "__main__":
    run_anomaly_detection()
