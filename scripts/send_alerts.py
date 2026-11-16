"""
Alerting Module for Retail & Supply Chain Control Tower.
Monitors:
1. Critical stock levels (Stockouts and imminent depletion)
2. Unexpected shipment delays (Supplier lead time anomalies)
Dispatches email alerts using standard SMTP (if configured) and logs all alerts in PostgreSQL.
"""
import sys
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from pathlib import Path
import pandas as pd

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from config.settings import (
    get_engine,
    SMTP_HOST,
    SMTP_PORT,
    SMTP_USER,
    SMTP_PASSWORD,
    ALERT_RECIPIENT_EMAIL,
    ENABLE_EMAIL_ALERTS
)

def check_critical_conditions(engine):
    """Queries database for critical stockouts and high-severity shipment delays."""
    with engine.connect() as conn:
        # Critical stock: current_stock == 0
        df_stockout = pd.read_sql("""
            SELECT 
                i.product_id, 
                p.product_name, 
                p.category, 
                i.current_stock, 
                i.reorder_point,
                s.supplier_name
            FROM inventory i
            JOIN products p ON i.product_id = p.product_id
            LEFT JOIN suppliers s ON p.supplier_id = s.supplier_id
            WHERE i.current_stock = 0 OR i.stock_status = 'OUT_OF_STOCK'
            ORDER BY p.product_id;
        """, conn)
        
        # Unexpected shipment delays
        df_delays = pd.read_sql("""
            SELECT 
                sh.shipment_id,
                sh.supplier_id,
                s.supplier_name,
                sh.product_id,
                p.product_name,
                sh.order_date,
                sh.expected_delivery_date,
                sh.delay_days,
                sh.lead_time_days
            FROM shipments sh
            JOIN suppliers s ON sh.supplier_id = s.supplier_id
            JOIN products p ON sh.product_id = p.product_id
            WHERE sh.is_delayed = TRUE AND (sh.delay_days >= 5 OR sh.shipping_status = 'DELAYED')
            ORDER BY sh.delay_days DESC
            LIMIT 10;
        """, conn)
        
    return df_stockout, df_delays

def format_alert_message(df_stockout, df_delays):
    """Formats HTML and plaintext alert messages."""
    stock_count = len(df_stockout)
    delay_count = len(df_delays)
    
    timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    subject = f"[CONTROL TOWER ALERT] {stock_count} Critical Stockouts & {delay_count} Shipment Delays Detected"
    
    # Plain text version
    lines = [
        f"RETAIL & SUPPLY CHAIN CONTROL TOWER - ALERT NOTIFICATION",
        f"Timestamp: {timestamp_str}",
        "=" * 60,
        f"\n1. CRITICAL STOCK-OUTS ({stock_count} products out of stock):"
    ]
    if stock_count > 0:
        for _, r in df_stockout.iterrows():
            lines.append(f"  - [{r['product_id']}] {r['product_name']} ({r['category']}) | Current Stock: 0 | Supplier: {r['supplier_name']}")
    else:
        lines.append("  All products have available stock.")
        
    lines.append(f"\n2. UNEXPECTED SHIPMENT DELAYS ({delay_count} shipments delayed):")
    if delay_count > 0:
        for _, r in df_delays.iterrows():
            lines.append(f"  - [{r['shipment_id']}] Supplier: {r['supplier_name']} | Product: {r['product_name']} | Delay: +{r['delay_days']} days | Lead Time: {r['lead_time_days']} days")
    else:
        lines.append("  No critical shipment delays detected.")
        
    lines.append("\n" + "=" * 60)
    lines.append("Action Required: Log in to Control Tower Dashboard to review reorder schedules.")
    plain_text = "\n".join(lines)
    
    # HTML version
    stock_rows_html = "".join([
        f"<tr><td><b>{r['product_id']}</b></td><td>{r['product_name']}</td><td>{r['category']}</td><td style='color:red;font-weight:bold;'>0</td><td>{r['supplier_name']}</td></tr>"
        for _, r in df_stockout.iterrows()
    ])
    
    delay_rows_html = "".join([
        f"<tr><td><b>{r['shipment_id']}</b></td><td>{r['supplier_name']}</td><td>{r['product_name']}</td><td style='color:#e67e22;font-weight:bold;'>+{r['delay_days']} days</td><td>{r['lead_time_days']} days</td></tr>"
        for _, r in df_delays.iterrows()
    ])
    
    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.5;">
        <div style="background-color: #1e3a8a; color: white; padding: 16px; border-radius: 6px;">
            <h2 style="margin: 0;">Retail & Supply Chain Control Tower</h2>
            <p style="margin: 4px 0 0 0; font-size: 13px; opacity: 0.9;">Automated Exception & Anomaly Alert • {timestamp_str}</p>
        </div>
        
        <h3 style="color: #b91c1c; margin-top: 24px;">🚨 Critical Stock-Outs ({stock_count} items)</h3>
        <table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse; width: 100%; border-color: #e5e7eb;">
            <tr style="background-color: #f9fafb; text-align: left;">
                <th>Product ID</th><th>Product Name</th><th>Category</th><th>Current Stock</th><th>Supplier</th>
            </tr>
            {stock_rows_html if stock_count > 0 else '<tr><td colspan="5">No stockouts detected.</td></tr>'}
        </table>

        <h3 style="color: #c2410c; margin-top: 24px;">⏱️ Unexpected Shipment Delays ({delay_count} shipments)</h3>
        <table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse; width: 100%; border-color: #e5e7eb;">
            <tr style="background-color: #f9fafb; text-align: left;">
                <th>Shipment ID</th><th>Supplier</th><th>Product</th><th>Delay</th><th>Lead Time</th>
            </tr>
            {delay_rows_html if delay_count > 0 else '<tr><td colspan="5">No shipment delays.</td></tr>'}
        </table>
        
        <p style="margin-top: 24px; font-size: 12px; color: #6b7280;">
            This is an automated notification generated by the Retail Control Tower pipeline.
        </p>
    </body>
    </html>
    """
    return subject, plain_text, html

def send_alert_notification():
    """Evaluates alerts and sends email or logs depending on configuration."""
    engine = get_engine()
    print("=" * 60)
    print("  RUNNING CONTROL TOWER ALERT MONITOR")
    print("=" * 60)
    
    df_stockout, df_delays = check_critical_conditions(engine)
    total_exceptions = len(df_stockout) + len(df_delays)
    
    if total_exceptions == 0:
        print("[✓] All inventory and shipment metrics healthy. No alerts triggered.")
        return
        
    subject, plain_text, html = format_alert_message(df_stockout, df_delays)
    print(f"[*] Alert Triggered: {subject}")
    
    delivery_status = "LOGGED_ONLY"
    
    # Check if SMTP email delivery is enabled
    if ENABLE_EMAIL_ALERTS and SMTP_USER and SMTP_PASSWORD:
        print(f"[*] Attempting SMTP email delivery via {SMTP_HOST}:{SMTP_PORT} to {ALERT_RECIPIENT_EMAIL}...")
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = SMTP_USER
            msg["To"] = ALERT_RECIPIENT_EMAIL
            
            msg.attach(MIMEText(plain_text, "plain"))
            msg.attach(MIMEText(html, "html"))
            
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as server:
                server.starttls()
                server.login(SMTP_USER, SMTP_PASSWORD)
                server.sendmail(SMTP_USER, ALERT_RECIPIENT_EMAIL, msg.as_string())
                
            delivery_status = "SENT"
            print(f"[✓] Email alert successfully sent to {ALERT_RECIPIENT_EMAIL}")
        except Exception as e:
            delivery_status = "FAILED"
            print(f"[!] SMTP Delivery failed: {e}")
            print("[*] Falling back to database alert logging.")
    else:
        print("[*] Email sending is disabled (ENABLE_EMAIL_ALERTS=false or SMTP unconfigured).")
        print("[*] Logging alert digest directly to console and database:")
        print("-" * 50)
        print(plain_text)
        print("-" * 50)
        
    # Log alert in alert_logs table in PostgreSQL
    with engine.begin() as conn:
        alert_record = pd.DataFrame([{
            "alert_type": "SUPPLY_CHAIN_EXCEPTION",
            "severity": "CRITICAL" if len(df_stockout) > 0 else "WARNING",
            "title": subject,
            "message": plain_text[:500] + "...",
            "recipient": ALERT_RECIPIENT_EMAIL if ENABLE_EMAIL_ALERTS else "CONSOLE/DB",
            "delivery_status": delivery_status,
            "created_at": datetime.now()
        }])
        alert_record.to_sql("alert_logs", conn, if_exists="append", index=False)
        
    print(f"[✓] Alert logged to PostgreSQL with status: {delivery_status}")
    print("=" * 60)

if __name__ == "__main__":
    send_alert_notification()

