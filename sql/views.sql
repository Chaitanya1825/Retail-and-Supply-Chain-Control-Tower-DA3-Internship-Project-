-- Control Tower Analytical Views for Superset and Visualizations

-- View 1: Top-line KPI summary (Latest snapshot)
CREATE OR REPLACE VIEW v_kpi_summary AS
SELECT 
    k.calculation_timestamp,
    k.total_products_monitored,
    k.stock_out_rate,
    k.on_time_delivery_pct,
    k.avg_supplier_lead_time,
    k.avg_days_of_inventory,
    k.out_of_stock_products,
    k.delayed_shipments_count,
    (SELECT COALESCE(SUM(current_stock), 0) FROM inventory) AS total_inventory_units
FROM kpi_metrics k
ORDER BY k.calculation_timestamp DESC
LIMIT 1;

-- View 2: Inventory Status Breakdown & Product Health
CREATE OR REPLACE VIEW v_inventory_status AS
SELECT 
    p.product_id,
    p.product_name,
    p.category,
    s.supplier_name,
    i.current_stock,
    i.reorder_point,
    i.safety_stock,
    i.stock_status,
    pk.days_of_inventory_remaining,
    pk.avg_daily_demand_30d,
    CASE 
        WHEN i.current_stock = 0 THEN 'Out of Stock'
        WHEN i.current_stock <= i.reorder_point THEN 'Low Stock (Action Needed)'
        ELSE 'Healthy Stock'
    END AS stock_health_status,
    i.last_updated
FROM inventory i
JOIN products p ON i.product_id = p.product_id
LEFT JOIN suppliers s ON p.supplier_id = s.supplier_id
LEFT JOIN product_kpis pk ON p.product_id = pk.product_id
ORDER BY i.current_stock ASC;

-- View 3: Shipment Performance and Delays
CREATE OR REPLACE VIEW v_shipment_performance AS
SELECT 
    sh.shipment_id,
    sh.order_date,
    sh.expected_delivery_date,
    sh.actual_delivery_date,
    sh.shipping_status,
    sh.is_delayed,
    sh.delay_days,
    sh.lead_time_days,
    sh.quantity_shipped,
    s.supplier_id,
    s.supplier_name,
    s.reliability_score,
    p.product_id,
    p.product_name,
    p.category
FROM shipments sh
JOIN suppliers s ON sh.supplier_id = s.supplier_id
JOIN products p ON sh.product_id = p.product_id
ORDER BY sh.order_date DESC;

-- View 4: Demand Forecasts vs Stockout Risk (Next 7 Days)
CREATE OR REPLACE VIEW v_demand_forecast_summary AS
SELECT 
    df.forecast_id,
    df.product_id,
    p.product_name,
    p.category,
    df.forecast_date,
    df.predicted_demand,
    df.confidence_lower,
    df.confidence_upper,
    df.current_stock,
    df.projected_stock_remaining,
    df.stockout_risk,
    p.reorder_point,
    s.supplier_name
FROM demand_forecasts df
JOIN products p ON df.product_id = p.product_id
LEFT JOIN suppliers s ON p.supplier_id = s.supplier_id
ORDER BY df.stockout_risk DESC, df.forecast_date ASC;

-- View 5: Anomaly Alerts Feed (Z-Scores)
CREATE OR REPLACE VIEW v_anomaly_feed AS
SELECT 
    a.anomaly_id,
    a.anomaly_type,
    a.reference_id,
    a.entity_name,
    a.metric_value,
    a.baseline_mean,
    a.baseline_std,
    a.z_score,
    a.severity,
    a.details,
    a.detected_at,
    a.status
FROM anomalies a
ORDER BY a.detected_at DESC;

-- View 6: What-If 7-Day Delay Scenario Impact
CREATE OR REPLACE VIEW v_what_if_delay_impact AS
SELECT 
    w.scenario_id,
    w.scenario_name,
    w.product_id,
    w.product_name,
    w.category,
    s.supplier_name,
    w.original_lead_time_days,
    w.simulated_lead_time_days,
    w.current_inventory,
    w.expected_demand_during_delay,
    w.projected_stockout_risk,
    w.estimated_units_shortage,
    w.impact_severity,
    w.analyzed_at
FROM what_if_scenarios w
LEFT JOIN suppliers s ON w.supplier_id = s.supplier_id
ORDER BY w.estimated_units_shortage DESC, w.current_inventory ASC;

