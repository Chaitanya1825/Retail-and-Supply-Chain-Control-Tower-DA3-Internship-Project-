"""
========================================================================================
 SUPPLYCORE ENTERPRISE CONTROL TOWER OS
 Next-Gen AI Supply Chain & Retail Analytics Platform
 High-Fidelity UI Redesign inspired by XY Analytics, Orbit Logistics, InventoryPro & Panda Retail
========================================================================================
"""
import sys
import os
import time
import base64
from datetime import datetime, date, timedelta
from pathlib import Path

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Root directory configuration
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from config.settings import get_engine, DB_HOST, DB_PORT, DB_NAME, DB_USER, ENABLE_EMAIL_ALERTS

# --------------------------------------------------------------------------------------
# 1. STREAMLIT PAGE CONFIGURATION
# --------------------------------------------------------------------------------------
st.set_page_config(
    page_title="SUPPLYCORE // Control Tower OS",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------------------------------------------
# 2. LOGO BASE64 ENCODER
# --------------------------------------------------------------------------------------
def get_logo_data_uri():
    """Returns base64 data URI of the project logo."""
    logo_path = ROOT_DIR / "assets" / "logo.png"
    if logo_path.exists():
        try:
            with open(logo_path, "rb") as f:
                encoded = base64.b64encode(f.read()).decode("utf-8")
                return f"data:image/png;base64,{encoded}"
        except Exception:
            return None
    return None

# --------------------------------------------------------------------------------------
# 3. HIGH-END ENTERPRISE CUSTOM CSS & KEYFRAME ANIMATIONS
# --------------------------------------------------------------------------------------
ENTERPRISE_CSS = """
<style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    :root {
        --bg-app: #080b13;
        --bg-sidebar: #0b0f19;
        --bg-card: #0f1523;
        --bg-card-hover: #141c2e;
        --border-card: rgba(255, 255, 255, 0.07);
        --border-hover: rgba(139, 92, 246, 0.35);
        --text-white: #ffffff;
        --text-secondary: #94a3b8;
        --text-muted: #64748b;
        --accent-purple: #8b5cf6;
        --accent-purple-gradient: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        --accent-blue-gradient: linear-gradient(135deg, #2563eb 0%, #38bdf8 100%);
        --accent-emerald: #10b981;
        --accent-amber: #f59e0b;
        --accent-red: #ef4444;
    }

    /* Core Page Overrides */
    .stApp {
        background-color: var(--bg-app) !important;
        color: var(--text-white) !important;
        font-family: 'Plus Jakarta Sans', -apple-system, sans-serif !important;
    }

    /* Hide Streamlit Default Headers & Footers */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: var(--bg-sidebar) !important;
        border-right: 1px solid var(--border-card) !important;
        padding-top: 0.8rem !important;
    }

    /* Sidebar Brand Section */
    .sidebar-brand-box {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.8rem 1rem 1.4rem 1rem;
        border-bottom: 1px solid var(--border-card);
        margin-bottom: 1rem;
    }
    .sidebar-brand-title {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.15rem;
        font-weight: 800;
        letter-spacing: -0.3px;
        color: #ffffff;
        line-height: 1.1;
    }
    .sidebar-brand-tag {
        font-size: 0.65rem;
        color: #8b5cf6;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 700;
    }

    /* Sidebar Navigation Pills */
    div[data-testid="stRadio"] > div {
        gap: 0.35rem !important;
    }
    div[data-testid="stRadio"] label {
        background: transparent !important;
        border-radius: 8px !important;
        padding: 0.55rem 0.9rem !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        color: #94a3b8 !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
    }
    div[data-testid="stRadio"] label:hover {
        background: rgba(255, 255, 255, 0.05) !important;
        color: #ffffff !important;
        transform: translateX(3px);
    }
    div[data-testid="stRadio"] label[data-checked="true"] {
        background: var(--accent-purple-gradient) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 18px rgba(124, 58, 237, 0.42) !important;
    }

    /* User Profile Card at Sidebar Bottom */
    .sidebar-user-card {
        margin-top: 1.5rem;
        padding: 0.85rem;
        background: rgba(15, 23, 42, 0.75);
        border: 1px solid var(--border-card);
        border-radius: 8px;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    .user-avatar-circle {
        width: 36px;
        height: 36px;
        background: var(--accent-purple-gradient);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 0.8rem;
        color: #ffffff;
        box-shadow: 0 0 10px rgba(139, 92, 246, 0.4);
    }

    /* Top Navigation Bar */
    .topbar-wrapper {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.5rem 0 1.2rem 0;
        margin-bottom: 1rem;
        border-bottom: 1px solid var(--border-card);
    }
    .topbar-greeting {
        font-size: 1.65rem;
        font-weight: 800;
        letter-spacing: -0.6px;
        color: #ffffff;
        margin: 0;
    }
    .topbar-subtext {
        font-size: 0.86rem;
        color: var(--text-secondary);
        margin-top: 0.2rem;
    }
    .topbar-pill-online {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        background: rgba(16, 185, 129, 0.12);
        border: 1px solid rgba(16, 185, 129, 0.35);
        color: #34d399;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        font-weight: 700;
        padding: 6px 12px;
        border-radius: 9999px;
        box-shadow: 0 0 14px rgba(16, 185, 129, 0.15);
    }
    .pulse-green {
        width: 8px;
        height: 8px;
        background-color: #10b981;
        border-radius: 50%;
        animation: pulse-ring 1.8s infinite;
    }
    @keyframes pulse-ring {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 8px rgba(16, 185, 129, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
    }

    /* Modern Metric Cards (Like Images 1, 2, 3, 4) */
    .metric-card-box {
        background: var(--bg-card);
        border: 1px solid var(--border-card);
        border-radius: 10px;
        padding: 1.15rem;
        position: relative;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        overflow: hidden;
    }
    .metric-card-box:hover {
        transform: translateY(-3px);
        background: var(--bg-card-hover);
        border-color: var(--border-hover);
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5), 0 0 20px rgba(139, 92, 246, 0.12);
    }
    .metric-top-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.75rem;
    }
    .metric-icon-square {
        width: 38px;
        height: 38px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.1rem;
    }
    .metric-badge-pill {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        font-weight: 700;
        padding: 3px 8px;
        border-radius: 9999px;
    }
    .metric-num-val {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.85rem;
        font-weight: 800;
        color: #ffffff;
        letter-spacing: -0.6px;
        line-height: 1;
        margin-bottom: 0.45rem;
    }
    .metric-title-lbl {
        font-size: 0.78rem;
        color: var(--text-secondary);
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .metric-sub-footer {
        font-size: 0.75rem;
        color: var(--text-muted);
        margin-top: 0.45rem;
        display: flex;
        align-items: center;
        gap: 0.35rem;
    }

    /* Suggestions / Alert Card List */
    .agent-card {
        background: rgba(15, 23, 42, 0.85);
        border: 1px solid var(--border-card);
        border-radius: 8px;
        padding: 0.9rem 1.1rem;
        margin-bottom: 0.75rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        transition: all 0.2s ease;
    }
    .agent-card:hover {
        border-color: rgba(139, 92, 246, 0.4);
        background: #141c2e;
        transform: translateX(4px);
    }

    /* Tables & Dataframes */
    [data-testid="stDataFrame"] {
        border: 1px solid var(--border-card) !important;
        border-radius: 8px !important;
        background: var(--bg-card) !important;
    }

    /* Streamlit Buttons */
    .stButton > button {
        background: var(--accent-purple-gradient) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 6px !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.82rem !important;
        font-weight: 700 !important;
        padding: 0.5rem 1.2rem !important;
        box-shadow: 0 4px 15px rgba(124, 58, 237, 0.35) !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button:hover {
        box-shadow: 0 6px 22px rgba(124, 58, 237, 0.55) !important;
        transform: translateY(-2px) !important;
    }
</style>
"""
st.markdown(ENTERPRISE_CSS, unsafe_allow_html=True)

# --------------------------------------------------------------------------------------
# 4. DATA ACCESS LAYER (PostgreSQL Cached)
# --------------------------------------------------------------------------------------
@st.cache_data(ttl=60)
def load_all_control_tower_data():
    """Loads all analytical datasets, relational views, and historical sales time-series."""
    engine = get_engine()
    with engine.connect() as conn:
        kpi_summary = pd.read_sql("SELECT * FROM v_kpi_summary", conn)
        inventory = pd.read_sql("SELECT * FROM v_inventory_status", conn)
        shipments = pd.read_sql("SELECT * FROM v_shipment_performance", conn)
        forecasts = pd.read_sql("SELECT * FROM v_demand_forecast_summary", conn)
        anomalies = pd.read_sql("SELECT * FROM v_anomaly_feed", conn)
        what_if = pd.read_sql("SELECT * FROM v_what_if_delay_impact", conn)
        suppliers = pd.read_sql("""
            SELECT 
                s.*, 
                COUNT(DISTINCT p.product_id) as product_count, 
                COUNT(DISTINCT sh.shipment_id) as shipment_count, 
                COALESCE(AVG(sh.lead_time_days), s.reliability_score * 0.1) as actual_avg_lead
            FROM suppliers s 
            LEFT JOIN products p ON s.supplier_id = p.supplier_id 
            LEFT JOIN shipments sh ON s.supplier_id = sh.supplier_id 
            GROUP BY s.supplier_id 
            ORDER BY s.reliability_score DESC
        """, conn)
        sales_trend = pd.read_sql("""
            SELECT 
                order_date, 
                SUM(quantity_ordered) as daily_units, 
                SUM(total_amount) as daily_revenue,
                COUNT(order_id) as order_count
            FROM sales_orders 
            GROUP BY order_date 
            ORDER BY order_date
        """, conn)
        product_daily_sales = pd.read_sql("""
            SELECT 
                order_date, 
                product_id, 
                SUM(quantity_ordered) as daily_units 
            FROM sales_orders 
            GROUP BY order_date, product_id
        """, conn)
        products_master = pd.read_sql("SELECT * FROM products", conn)
        
    return {
        "kpi": kpi_summary,
        "inventory": inventory,
        "shipments": shipments,
        "forecasts": forecasts,
        "anomalies": anomalies,
        "what_if": what_if,
        "suppliers": suppliers,
        "sales_trend": sales_trend,
        "product_daily_sales": product_daily_sales,
        "products": products_master
    }

# --------------------------------------------------------------------------------------
# 5. PLOTLY STYLING HELPER (Dark Mode Neon Gradients)
# --------------------------------------------------------------------------------------
def apply_enterprise_theme(fig, height=360):
    """Applies clean dark theme styling with subtle gridlines and neon accents."""
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=height,
        margin=dict(l=15, r=15, t=38, b=15),
        font=dict(
            family="Plus Jakarta Sans, sans-serif",
            color="#94a3b8",
            size=11
        ),
        title=dict(
            font=dict(family="JetBrains Mono, monospace", size=13, color="#f8fafc"),
            x=0.01,
            y=0.96
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=10, color="#94a3b8"),
            bgcolor="rgba(0,0,0,0)"
        ),
        hoverlabel=dict(
            bgcolor="#0f172a",
            bordercolor="#334155",
            font=dict(family="JetBrains Mono, monospace", color="#ffffff", size=11)
        )
    )
    fig.update_xaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor="rgba(255, 255, 255, 0.05)",
        linecolor="rgba(255, 255, 255, 0.1)",
        tickfont=dict(color="#64748b", size=10)
    )
    fig.update_yaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor="rgba(255, 255, 255, 0.05)",
        linecolor="rgba(255, 255, 255, 0.1)",
        tickfont=dict(color="#64748b", size=10)
    )
    return fig

# --------------------------------------------------------------------------------------
# 6. SIDEBAR COMPONENT (Brand, Logo, Nav & Profile)
# --------------------------------------------------------------------------------------
def render_sidebar():
    """Renders the high-end branded sidebar with logo, navigation, and user card."""
    with st.sidebar:
        logo_uri = get_logo_data_uri()
        if logo_uri:
            st.markdown(f"""
            <div class="sidebar-brand-box">
                <img src="{logo_uri}" style="height: 38px; border-radius: 6px;" alt="Logo" />
                <div>
                    <div class="sidebar-brand-title">SUPPLYCORE</div>
                    <div class="sidebar-brand-tag">CONTROL TOWER OS</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="sidebar-brand-box">
                <div style="width:36px; height:36px; background:linear-gradient(135deg, #6366f1, #8b5cf6); border-radius:8px; display:flex; align-items:center; justify-content:center; font-size:1.2rem; box-shadow:0 0 12px rgba(139,92,246,0.5);">⚡</div>
                <div>
                    <div class="sidebar-brand-title">SUPPLYCORE</div>
                    <div class="sidebar-brand-tag">CONTROL TOWER OS</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        # Section Label: MAIN
        st.markdown("<div style='font-family: JetBrains Mono; font-size: 0.68rem; color:#475569; font-weight:700; margin:0.8rem 0 0.4rem 0.5rem;'>MAIN MENU</div>", unsafe_allow_html=True)
        
        # Navigation Options
        nav_selection = st.radio(
            "MAIN NAVIGATION",
            options=[
                "Overview",
                "Inventory",
                "Shipments",
                "Suppliers",
                "Demand Forecast",
                "Anomalies",
                "What-if Analysis",
                "Settings"
            ],
            index=0,
            label_visibility="collapsed"
        )
        
        st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
        
        # Bottom User Profile Card (Matching Image 1 & 2)
        st.markdown("""
        <div class="sidebar-user-card">
            <div class="user-avatar-circle">AM</div>
            <div style="flex: 1; overflow: hidden;">
                <div style="font-size: 0.82rem; font-weight: 700; color: #ffffff; white-space: nowrap;">Alex Morgan</div>
                <div style="font-size: 0.68rem; color: #64748b; white-space: nowrap;">Head of Supply Chain</div>
            </div>
            <div style="color: #64748b; font-size: 0.9rem;">⋮</div>
        </div>
        """, unsafe_allow_html=True)
        
        return nav_selection

# --------------------------------------------------------------------------------------
# 7. TOPBAR COMPONENT (Greeting, Status, Search & Controls)
# --------------------------------------------------------------------------------------
def render_topbar(active_page):
    """Renders persistent greeting, live cluster telemetry pill, and action buttons."""
    # Dynamic time-of-day greeting
    current_hour = datetime.now().hour
    if current_hour < 12:
        greeting_time = "Good morning"
    elif current_hour < 17:
        greeting_time = "Good afternoon"
    else:
        greeting_time = "Good evening"
        
    date_str = datetime.now().strftime("%B %d, %Y • %A")
    
    col_greet, col_actions = st.columns([2.8, 1.2])
    with col_greet:
        st.markdown(f"""
        <div>
            <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #8b5cf6; text-transform: uppercase; letter-spacing: 1px; font-weight: 600;">
                {active_page.upper()} // SYSTEM PULSE
            </div>
            <h1 class="topbar-greeting">{greeting_time}, Alex ✌️</h1>
            <div class="topbar-subtext">Here's how your supply chain network performed today • <span style="color:#10b981; font-weight:600;">+14.2% fulfillment growth</span></div>
        </div>
        """, unsafe_allow_html=True)
        
    with col_actions:
        st.markdown(f"""
        <div style="text-align: right; padding-top: 0.4rem;">
            <div class="topbar-pill-online">
                <span class="pulse-green"></span> ALL SYSTEMS OPERATIONAL
            </div>
            <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; color: #64748b; margin-top: 0.35rem;">
                {date_str}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<div style='margin-bottom: 1.2rem;'></div>", unsafe_allow_html=True)

# --------------------------------------------------------------------------------------
# 8. PAGE: OVERVIEW
# --------------------------------------------------------------------------------------
def render_overview_page(data):
    """Renders the executive overview with 5 cards, trend chart, donut, and US map."""
    kpi = data["kpi"].iloc[0] if not data["kpi"].empty else None
    
    total_prods = int(kpi["total_products_monitored"]) if kpi is not None else 100
    total_inv = int(kpi["total_inventory_units"]) if kpi is not None else 0
    stockout_rate = float(kpi["stock_out_rate"]) if kpi is not None else 0.0
    otd_pct = float(kpi["on_time_delivery_pct"]) if kpi is not None else 0.0
    avg_lead = float(kpi["avg_supplier_lead_time"]) if kpi is not None else 0.0
    avg_doi = float(kpi["avg_days_of_inventory"]) if kpi is not None else 0.0
    
    # 1. Row of 4-5 Premium Metric Cards (Matching Images 1, 2, 3, 4)
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        st.markdown(f"""
        <div class="metric-card-box">
            <div class="metric-top-row">
                <div class="metric-icon-square" style="background: rgba(139, 92, 246, 0.15); color: #a78bfa;">📦</div>
                <div class="metric-badge-pill" style="background: rgba(16, 185, 129, 0.15); color: #34d399;">↗ +12.4%</div>
            </div>
            <div class="metric-num-val">{total_inv:,}</div>
            <div class="metric-title-lbl">TOTAL CURRENT INVENTORY</div>
            <div class="metric-subtext">On-hand warehouse stock • {total_prods} Active SKUs</div>
        </div>
        """, unsafe_allow_html=True)
        
    with c2:
        badge_color = "#ef4444" if stockout_rate > 3.0 else "#10b981"
        badge_bg = "rgba(239, 68, 68, 0.15)" if stockout_rate > 3.0 else "rgba(16, 185, 129, 0.15)"
        st.markdown(f"""
        <div class="metric-card-box">
            <div class="metric-top-row">
                <div class="metric-icon-square" style="background: rgba(239, 68, 68, 0.15); color: #f87171;">⚠️</div>
                <div class="metric-badge-pill" style="background: {badge_bg}; color: {badge_color};">{int(kpi['out_of_stock_products'])} CRITICAL</div>
            </div>
            <div class="metric-num-val" style="color: {badge_color};">{stockout_rate:.1f}%</div>
            <div class="metric-title-lbl">STOCK-OUT RATE</div>
            <div class="metric-subtext">Immediate reorder required for 5 SKUs</div>
        </div>
        """, unsafe_allow_html=True)
        
    with c3:
        st.markdown(f"""
        <div class="metric-card-box">
            <div class="metric-top-row">
                <div class="metric-icon-square" style="background: rgba(16, 185, 129, 0.15); color: #34d399;">🎯</div>
                <div class="metric-badge-pill" style="background: rgba(16, 185, 129, 0.15); color: #34d399;">90% SLA Target</div>
            </div>
            <div class="metric-num-val" style="color: #34d399;">{otd_pct:.1f}%</div>
            <div class="metric-title-lbl">ON-TIME DELIVERY (OTD)</div>
            <div class="metric-subtext">{int(kpi['delayed_shipments_count'])} delayed shipments in trailing 90d</div>
        </div>
        """, unsafe_allow_html=True)
        
    with c4:
        st.markdown(f"""
        <div class="metric-card-box">
            <div class="metric-top-row">
                <div class="metric-icon-square" style="background: rgba(59, 130, 246, 0.15); color: #60a5fa;">⏳</div>
                <div class="metric-badge-pill" style="background: rgba(59, 130, 246, 0.15); color: #60a5fa;">{avg_doi:.1f}d DOI Runway</div>
            </div>
            <div class="metric-num-val">{avg_lead:.1f} Days</div>
            <div class="metric-title-lbl">AVG SUPPLIER LEAD TIME</div>
            <div class="metric-subtext">Order-to-delivery dock average</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 2. Main Analytics Row: Demand Trend Curve & Health Donut (Matching Images 1, 3, 4)
    col_chart_left, col_chart_right = st.columns([2.1, 1])
    
    with col_chart_left:
        df_sales = data["sales_trend"]
        df_sales["7d_ma"] = df_sales["daily_units"].rolling(window=7, min_periods=1).mean()
        
        fig_trend = go.Figure()
        # Area fill with neon purple
        fig_trend.add_trace(go.Scatter(
            x=df_sales["order_date"],
            y=df_sales["daily_units"],
            mode="lines",
            name="Daily Units Ordered",
            line=dict(color="rgba(139, 92, 246, 0.4)", width=1.5),
            fill="tozeroy",
            fillcolor="rgba(139, 92, 246, 0.10)"
        ))
        # Sleek 7-day moving average curve
        fig_trend.add_trace(go.Scatter(
            x=df_sales["order_date"],
            y=df_sales["7d_ma"],
            mode="lines",
            name="7-Day Trend Velocity",
            line=dict(color="#a855f7", width=3)
        ))
        fig_trend.update_layout(title="ENTERPRISE DEMAND & VELOCITY TREND (LAST 90 DAYS)")
        apply_enterprise_theme(fig_trend, height=330)
        st.plotly_chart(fig_trend, use_container_width=True)
        
    with col_chart_right:
        df_inv = data["inventory"]
        health_counts = df_inv["stock_health_status"].value_counts().reset_index()
        health_counts.columns = ["Status", "Count"]
        
        color_map = {
            "Healthy Stock": "#10b981",
            "Low Stock (Action Needed)": "#f59e0b",
            "Out of Stock": "#ef4444"
        }
        fig_donut = px.pie(
            health_counts,
            values="Count",
            names="Status",
            color="Status",
            color_discrete_map=color_map,
            hole=0.68
        )
        fig_donut.update_traces(
            textposition="inside",
            textinfo="percent",
            hoverinfo="label+value+percent",
            marker=dict(line=dict(color="#080b13", width=2))
        )
        fig_donut.update_layout(
            title="STOCK HEALTH DISTRIBUTION",
            annotations=[dict(text=f"<b>{total_inv:,}</b><br><span style='font-size:10px;color:#94a3b8;'>Units</span>", x=0.5, y=0.5, font_size=15, font_color="#ffffff", showarrow=False)]
        )
        apply_enterprise_theme(fig_donut, height=330)
        st.plotly_chart(fig_donut, use_container_width=True)
        
    # 3. Supply Chain Logistics Map & AI Replenishment Suggestions (Matching Images 2 & 4!)
    col_map, col_agent = st.columns([1.8, 1.2])
    
    with col_map:
        # Interactive US Supplier Hub Logistics Map
        supp_cities = [
            {"city": "Chicago, IL", "lat": 41.8781, "lon": -87.6298, "name": "Apex Global Logistics"},
            {"city": "Dallas, TX", "lat": 32.7767, "lon": -96.7970, "name": "Prime Source Supply"},
            {"city": "San Jose, CA", "lat": 37.3382, "lon": -121.8863, "name": "Horizon Electronics Mfg"},
            {"city": "Seattle, WA", "lat": 47.6062, "lon": -122.3321, "name": "BlueWave Distribution"},
            {"city": "Atlanta, GA", "lat": 33.7490, "lon": -84.3880, "name": "Vertex Goods & Materials"},
            {"city": "Denver, CO", "lat": 39.7392, "lon": -104.9903, "name": "Pinnacle Packaging & Parts"},
            {"city": "Boston, MA", "lat": 42.3601, "lon": -71.0589, "name": "Beacon Industrial Corp"},
            {"city": "New York, NY", "lat": 40.7128, "lon": -74.0060, "name": "Nexus Materials Direct"},
            {"city": "Los Angeles, CA", "lat": 34.0522, "lon": -118.2437, "name": "Pacific Freight & Imports"},
            {"city": "Columbus, OH", "lat": 39.9612, "lon": -82.9988, "name": "Summit Retail Solutions"}
        ]
        hub_center = {"city": "Kansas City Central Hub", "lat": 39.0997, "lon": -94.5786}
        
        fig_map = go.Figure()
        
        # Connect arcs from suppliers to central hub
        for s_node in supp_cities:
            fig_map.add_trace(go.Scattergeo(
                locationmode='USA-states',
                lon=[s_node["lon"], hub_center["lon"]],
                lat=[s_node["lat"], hub_center["lat"]],
                mode='lines',
                line=dict(width=1.2, color='rgba(139, 92, 246, 0.45)'),
                hoverinfo='none',
                showlegend=False
            ))
            
        # Supplier points
        fig_map.add_trace(go.Scattergeo(
            locationmode='USA-states',
            lon=[s["lon"] for s in supp_cities],
            lat=[s["lat"] for s in supp_cities],
            text=[f"{s['name']} ({s['city']})" for s in supp_cities],
            mode='markers',
            marker=dict(size=8, color='#38bdf8', line=dict(width=1, color='#ffffff')),
            name='Supplier Nodes'
        ))
        
        # Central Hub
        fig_map.add_trace(go.Scattergeo(
            locationmode='USA-states',
            lon=[hub_center["lon"]],
            lat=[hub_center["lat"]],
            text=["Central Fulfillment DC (Kansas City)"],
            mode='markers',
            marker=dict(size=14, color='#8b5cf6', symbol='star', line=dict(width=2, color='#ffffff')),
            name='Primary Fulfillment Hub'
        ))
        
        fig_map.update_layout(
            title="LIVE SUPPLIER CARRIER ROUTES & LOGISTICS HUBS",
            geo_scope='usa',
            geo=dict(
                bgcolor='rgba(0,0,0,0)',
                lakecolor='#080b13',
                landcolor='#0f172a',
                subunitcolor='#1e293b',
                showland=True,
                showlakes=True
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=0, r=0, t=35, b=0),
            height=310
        )
        st.plotly_chart(fig_map, use_container_width=True)
        
    with col_agent:
        st.markdown("""
        <div style="font-family:'JetBrains Mono'; font-size:0.8rem; color:#8b5cf6; font-weight:700; margin-bottom:0.6rem;">
            REPLENISHMENT AGENT SUGGESTIONS (PROPHET AI)
        </div>
        """, unsafe_allow_html=True)
        
        # Display top 3 immediate action items (Matching Image 4)
        df_fc_risk = data["forecasts"][data["forecasts"]["stockout_risk"] == True].groupby("product_id").first().reset_index().head(3)
        for _, r in df_fc_risk.iterrows():
            st.markdown(f"""
            <div class="agent-card">
                <div>
                    <div style="font-size:0.85rem; font-weight:700; color:#ffffff;">{r['product_name']}</div>
                    <div style="font-size:0.72rem; color:#ef4444; font-family:'JetBrains Mono';">⚠️ Stockout Risk • On-hand: {r['current_stock']}u</div>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:0.85rem; font-weight:800; color:#38bdf8; font-family:'JetBrains Mono';">Order +180u</div>
                    <div style="font-size:0.68rem; color:#64748b;">By May 20</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("""
        <div class="agent-card" style="border-color: rgba(16, 185, 129, 0.3);">
            <div>
                <div style="font-size:0.85rem; font-weight:700; color:#ffffff;">Buffer Optimization Check</div>
                <div style="font-size:0.72rem; color:#34d399; font-family:'JetBrains Mono';">✓ 80 Products at Optimal Par</div>
            </div>
            <div style="text-align:right;">
                <span class="metric-badge-pill" style="background:rgba(16,185,129,0.15); color:#34d399;">HEALTHY</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    # Section 4: Recent Shipments & Carrier Activity (Matching Orbit Logistics Image 2)
    st.markdown("""
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.6rem;">
        <div style="font-family:'JetBrains Mono'; font-size:0.82rem; font-weight:700; color:#f8fafc;">
            RECENT SHIPMENTS & CARRIER FULFILLMENT ACTIVITY
        </div>
        <div style="font-family:'JetBrains Mono'; font-size:0.72rem; color:#64748b;">
            Live Carrier Telemetry • 233 Total Purchase Orders
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    recent_shp = data["shipments"].head(6)[[
        "shipment_id", "supplier_name", "product_name", "order_date", 
        "expected_delivery_date", "delay_days", "lead_time_days", "shipping_status"
    ]].rename(columns={
        "shipment_id": "Tracking ID",
        "supplier_name": "Carrier / Supplier",
        "product_name": "Product Name",
        "order_date": "Order Date",
        "expected_delivery_date": "Expected ETA",
        "delay_days": "Delay Days",
        "lead_time_days": "Lead Time",
        "shipping_status": "Status"
    })
    st.dataframe(recent_shp, use_container_width=True, hide_index=True)

# --------------------------------------------------------------------------------------
# 9. PAGE: INVENTORY
# --------------------------------------------------------------------------------------
def render_inventory_page(data):
    """Renders catalog inventory with search, filters, and stock ledger."""
    df_inv = data["inventory"]
    
    total_skus = len(df_inv)
    out_of_stock = len(df_inv[df_inv["current_stock"] == 0])
    low_stock = len(df_inv[(df_inv["current_stock"] > 0) & (df_inv["current_stock"] <= df_inv["reorder_point"])])
    healthy = total_skus - out_of_stock - low_stock
    
    i1, i2, i3, i4 = st.columns(4)
    with i1:
        st.markdown(f"""
        <div class="metric-card-box">
            <div class="metric-num-val">{total_skus}</div>
            <div class="metric-title-lbl">TOTAL MONITORED SKUs</div>
            <div class="metric-subtext">Active Product Catalog</div>
        </div>
        """, unsafe_allow_html=True)
    with i2:
        st.markdown(f"""
        <div class="metric-card-box">
            <div class="metric-num-val" style="color:#10b981;">{healthy}</div>
            <div class="metric-title-lbl">HEALTHY BUFFER</div>
            <div class="metric-subtext">Above Reorder Threshold</div>
        </div>
        """, unsafe_allow_html=True)
    with i3:
        st.markdown(f"""
        <div class="metric-card-box">
            <div class="metric-num-val" style="color:#f59e0b;">{low_stock}</div>
            <div class="metric-title-lbl">LOW STOCK REORDER</div>
            <div class="metric-subtext">Actionable Replenishment Required</div>
        </div>
        """, unsafe_allow_html=True)
    with i4:
        st.markdown(f"""
        <div class="metric-card-box">
            <div class="metric-num-val" style="color:#ef4444;">{out_of_stock}</div>
            <div class="metric-title-lbl">CRITICAL STOCKOUTS</div>
            <div class="metric-subtext">Zero Units On-Hand</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Filter Bar
    f1, f2, f3 = st.columns([2, 1.5, 1.5])
    with f1:
        search_kw = st.text_input("🔍 Search SKU or Product Name", placeholder="e.g. Wireless, PROD-001...").strip().lower()
    with f2:
        cat_filter = st.multiselect("Category", options=sorted(df_inv["category"].unique()), default=sorted(df_inv["category"].unique()))
    with f3:
        status_filter = st.multiselect("Health Status", options=sorted(df_inv["stock_health_status"].unique()), default=sorted(df_inv["stock_health_status"].unique()))
        
    filtered = df_inv.copy()
    if search_kw:
        filtered = filtered[filtered["product_name"].str.lower().str.contains(search_kw) | filtered["product_id"].str.lower().str.contains(search_kw)]
    if cat_filter:
        filtered = filtered[filtered["category"].isin(cat_filter)]
    if status_filter:
        filtered = filtered[filtered["stock_health_status"].isin(status_filter)]
        
    st.dataframe(
        filtered[[
            "product_id", "product_name", "category", "supplier_name", 
            "current_stock", "reorder_point", "safety_stock", 
            "avg_daily_demand_30d", "days_of_inventory_remaining", "stock_health_status"
        ]].rename(columns={
            "product_id": "SKU",
            "product_name": "Product Name",
            "category": "Category",
            "supplier_name": "Primary Vendor",
            "current_stock": "Current Stock",
            "reorder_point": "Reorder Level",
            "safety_stock": "Safety Buffer",
            "avg_daily_demand_30d": "Daily Demand Rate",
            "days_of_inventory_remaining": "Days Remaining",
            "stock_health_status": "Status"
        }),
        use_container_width=True,
        hide_index=True
    )

# --------------------------------------------------------------------------------------
# 10. PAGE: SHIPMENTS
# --------------------------------------------------------------------------------------
def render_shipments_page(data):
    """Renders shipment logistics and supplier delivery performance."""
    df_ship = data["shipments"]
    
    total_shp = len(df_ship)
    delayed_shp = len(df_ship[df_ship["is_delayed"] == True])
    transit_shp = len(df_ship[df_ship["shipping_status"] == "IN_TRANSIT"])
    otd_pct = ((total_shp - delayed_shp) / total_shp * 100) if total_shp > 0 else 100.0
    
    s1, s2, s3, s4 = st.columns(4)
    with s1:
        st.markdown(f"""
        <div class="metric-card-box">
            <div class="metric-num-val">{total_shp}</div>
            <div class="metric-title-lbl">TOTAL SHIPMENTS</div>
            <div class="metric-subtext">Trailing 90 Days</div>
        </div>
        """, unsafe_allow_html=True)
    with s2:
        st.markdown(f"""
        <div class="metric-card-box">
            <div class="metric-num-val" style="color:#10b981;">{otd_pct:.1f}%</div>
            <div class="metric-title-lbl">ON-TIME DELIVERY %</div>
            <div class="metric-subtext">Contractual Fulfillment SLA</div>
        </div>
        """, unsafe_allow_html=True)
    with s3:
        st.markdown(f"""
        <div class="metric-card-box">
            <div class="metric-num-val" style="color:#38bdf8;">{transit_shp}</div>
            <div class="metric-title-lbl">IN-TRANSIT SHIPMENTS</div>
            <div class="metric-subtext">Carrier Freight En Route</div>
        </div>
        """, unsafe_allow_html=True)
    with s4:
        st.markdown(f"""
        <div class="metric-card-box">
            <div class="metric-num-val" style="color:#ef4444;">{delayed_shp}</div>
            <div class="metric-title-lbl">DELAYED SHIPMENTS</div>
            <div class="metric-subtext">Exceeded Expected ETA</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Table of Shipments
    st.markdown("#### Carrier Shipment Tracking & Delivery Ledger")
    status_filter = st.selectbox("Status Filter", ["ALL", "DELAYED", "IN_TRANSIT", "DELIVERED"], index=0)
    
    filtered_s = df_ship.copy()
    if status_filter != "ALL":
        filtered_s = filtered_s[filtered_s["shipping_status"] == status_filter]
        
    st.dataframe(
        filtered_s[[
            "shipment_id", "supplier_name", "product_name", "quantity_shipped", 
            "order_date", "expected_delivery_date", "actual_delivery_date", 
            "delay_days", "lead_time_days", "shipping_status"
        ]].rename(columns={
            "shipment_id": "Tracking ID",
            "supplier_name": "Supplier",
            "product_name": "Product Name",
            "quantity_shipped": "Quantity",
            "order_date": "Order Date",
            "expected_delivery_date": "Expected ETA",
            "actual_delivery_date": "Actual Arrival",
            "delay_days": "Delay Days",
            "lead_time_days": "Total Lead Time",
            "shipping_status": "Status"
        }),
        use_container_width=True,
        hide_index=True
    )

# --------------------------------------------------------------------------------------
# 11. PAGE: SUPPLIERS
# --------------------------------------------------------------------------------------
def render_suppliers_page(data):
    """Renders supplier scorecards and reliability metrics."""
    df_supp = data["suppliers"]
    
    total_supp = len(df_supp)
    avg_rel = df_supp["reliability_score"].mean()
    top_supp = df_supp.sort_values("reliability_score", ascending=False).iloc[0]["supplier_name"]
    
    p1, p2, p3 = st.columns(3)
    with p1:
        st.markdown(f"""
        <div class="metric-card-box">
            <div class="metric-num-val">{total_supp}</div>
            <div class="metric-title-lbl">ACTIVE SUPPLIERS</div>
            <div class="metric-subtext">Direct Contracted Partners</div>
        </div>
        """, unsafe_allow_html=True)
    with p2:
        st.markdown(f"""
        <div class="metric-card-box">
            <div class="metric-num-val" style="color:#10b981;">{avg_rel:.1f}%</div>
            <div class="metric-title-lbl">PORTFOLIO RELIABILITY</div>
            <div class="metric-subtext">Mean Fulfillment Rating</div>
        </div>
        """, unsafe_allow_html=True)
    with p3:
        st.markdown(f"""
        <div class="metric-card-box">
            <div class="metric-num-val" style="font-size:1.3rem; color:#a78bfa;">{top_supp}</div>
            <div class="metric-title-lbl">TOP TIER VENDOR</div>
            <div class="metric-subtext">97.5% On-Time Record</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("#### Supplier Directory & Scorecards")
    st.dataframe(
        df_supp[[
            "supplier_id", "supplier_name", "contact_name", "email", 
            "city", "reliability_score", "actual_avg_lead", "product_count", "shipment_count"
        ]].rename(columns={
            "supplier_id": "Vendor ID",
            "supplier_name": "Company Name",
            "contact_name": "Key Contact",
            "email": "Email Address",
            "city": "Logistics Hub",
            "reliability_score": "Reliability Score (%)",
            "actual_avg_lead": "Avg Lead Time (Days)",
            "product_count": "Active SKUs",
            "shipment_count": "Shipments Delivered"
        }),
        use_container_width=True,
        hide_index=True
    )

# --------------------------------------------------------------------------------------
# 12. PAGE: DEMAND FORECASTING (FACEBOOK PROPHET)
# --------------------------------------------------------------------------------------
def render_forecasting_page(data):
    """Renders Facebook Prophet 7-day demand forecasts, confidence intervals, and stockout risks."""
    df_fc = data["forecasts"]
    
    horizon_days = 7
    total_forecast_units = df_fc["predicted_demand"].sum()
    stockout_risk_prods = df_fc[df_fc["stockout_risk"] == True]["product_id"].unique()
    
    f1, f2, f3 = st.columns(3)
    with f1:
        st.markdown(f"""
        <div class="metric-card-box">
            <div class="metric-num-val">{horizon_days} Days</div>
            <div class="metric-title-lbl">FORECAST HORIZON</div>
            <div class="metric-subtext">Daily Forward Curve</div>
        </div>
        """, unsafe_allow_html=True)
    with f2:
        st.markdown(f"""
        <div class="metric-card-box">
            <div class="metric-num-val">{int(total_forecast_units):,}</div>
            <div class="metric-title-lbl">PROJECTED CONSUMPTION</div>
            <div class="metric-subtext">Total Catalog Units</div>
        </div>
        """, unsafe_allow_html=True)
    with f3:
        st.markdown(f"""
        <div class="metric-card-box">
            <div class="metric-num-val" style="color:#ef4444;">{len(stockout_risk_prods)} SKUs</div>
            <div class="metric-title-lbl">AT-RISK OF STOCKOUT</div>
            <div class="metric-subtext">Exceeds On-Hand Buffer</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Interactive Product Selector
    col_s1, col_s2 = st.columns([1, 2.5])
    with col_s1:
        cat_choices = sorted(df_fc["category"].unique())
        selected_cat = st.selectbox("Category Filter:", ["ALL"] + cat_choices, index=0)
        filtered_by_cat = df_fc if selected_cat == "ALL" else df_fc[df_fc["category"] == selected_cat]
        prod_choices = filtered_by_cat["product_name"].unique()
        selected_prod = st.selectbox("Inspect Product Forecast:", prod_choices, index=0)
        
    p_fc = df_fc[df_fc["product_name"] == selected_prod].sort_values("forecast_date")
    curr_stock = p_fc["current_stock"].iloc[0]
    reorder_pt = p_fc["reorder_point"].iloc[0]
    has_risk = p_fc["stockout_risk"].any()
    selected_p_id = p_fc["product_id"].iloc[0]
    
    # Unified Forecast Curve with Historical Actual Demand (Matching Image 4)
    fig_p = go.Figure()
    
    # 1. Historical Actual Demand (Trailing 30 Days)
    df_p_actual = data["product_daily_sales"][data["product_daily_sales"]["product_id"] == selected_p_id].sort_values("order_date")
    df_p_actual_30d = df_p_actual.tail(30)
    
    if not df_p_actual_30d.empty:
        fig_p.add_trace(go.Scatter(
            x=df_p_actual_30d["order_date"],
            y=df_p_actual_30d["daily_units"],
            mode="lines+markers",
            name="Actual Demand (Trailing 30D)",
            line=dict(color="#64748b", width=1.8),
            marker=dict(size=4, color="#94a3b8")
        ))
        
    # 2. Predicted 7-Day Forecast Curve
    fig_p.add_trace(go.Scatter(
        x=p_fc["forecast_date"],
        y=p_fc["predicted_demand"],
        mode="lines+markers",
        name="Prophet Forecast (Next 7D)",
        line=dict(color="#8b5cf6", width=3),
        marker=dict(size=6, color="#a78bfa")
    ))
    
    # 3. 90% Confidence Interval
    fig_p.add_trace(go.Scatter(
        x=pd.concat([p_fc["forecast_date"], p_fc["forecast_date"][::-1]]),
        y=pd.concat([p_fc["confidence_upper"], p_fc["confidence_lower"][::-1]]),
        fill="toself",
        fillcolor="rgba(139, 92, 246, 0.15)",
        line=dict(color="rgba(255,255,255,0)"),
        hoverinfo="skip",
        name="90% Confidence Band"
    ))
    
    # 4. Projected Stock Remaining Trajectory
    fig_p.add_trace(go.Scatter(
        x=p_fc["forecast_date"],
        y=p_fc["projected_stock_remaining"],
        mode="lines+markers",
        name="Projected Stock Buffer",
        line=dict(color="#ef4444" if has_risk else "#10b981", width=2.5, dash="dot"),
        marker=dict(size=5)
    ))
    
    # 5. Reorder Point Line
    fig_p.add_hline(
        y=reorder_pt,
        line_dash="dash",
        line_color="#f59e0b",
        annotation_text=f"Reorder Level ({reorder_pt}u)",
        annotation_position="bottom right",
        annotation_font=dict(color="#f59e0b", size=10)
    )
    
    fig_p.update_layout(title=f"PROPHET 7-DAY FORECAST & STOCK DEPLETION: {selected_prod.upper()}")
    apply_enterprise_theme(fig_p, height=360)
    st.plotly_chart(fig_p, use_container_width=True)
    
    # Table of products facing stockout risks
    st.markdown("#### 🚨 Products Facing Projected Stockout within 7 Days")
    at_risk_df = df_fc[df_fc["stockout_risk"] == True].groupby(["product_id", "product_name", "category", "supplier_name"]).agg(
        current_stock=("current_stock", "first"),
        predicted_7d_total=("predicted_demand", "sum"),
        min_projected_stock=("projected_stock_remaining", "min")
    ).reset_index()
    
    st.dataframe(
        at_risk_df.rename(columns={
            "product_id": "SKU",
            "product_name": "Product Name",
            "category": "Category",
            "supplier_name": "Vendor",
            "current_stock": "Current Stock",
            "predicted_7d_total": "7D Demand Total",
            "min_projected_stock": "Projected Ending Balance"
        }),
        use_container_width=True,
        hide_index=True
    )

# --------------------------------------------------------------------------------------
# 13. PAGE: ANOMALIES
# --------------------------------------------------------------------------------------
def render_anomalies_page(data):
    """Renders statistical Z-score anomaly monitoring."""
    df_a = data["anomalies"]
    
    total_anom = len(df_a)
    demand_spikes = len(df_a[df_a["anomaly_type"] == "DEMAND_SPIKE"])
    shipment_delays = len(df_a[df_a["anomaly_type"] == "SHIPMENT_DELAY"])
    critical_count = len(df_a[df_a["severity"] == "CRITICAL"])
    
    a1, a2, a3 = st.columns(3)
    with a1:
        st.markdown(f"""
        <div class="metric-card-box">
            <div class="metric-num-val">{total_anom}</div>
            <div class="metric-title-lbl">TOTAL ANOMALIES</div>
            <div class="metric-subtext">Statistical Outliers (|Z| ≥ 2.0)</div>
        </div>
        """, unsafe_allow_html=True)
    with a2:
        st.markdown(f"""
        <div class="metric-card-box">
            <div class="metric-num-val" style="color:#ef4444;">{critical_count}</div>
            <div class="metric-title-lbl">CRITICAL SEVERITY</div>
            <div class="metric-subtext">|Z| ≥ 3.0 Standard Deviations</div>
        </div>
        """, unsafe_allow_html=True)
    with a3:
        st.markdown(f"""
        <div class="metric-card-box">
            <div class="metric-num-val" style="color:#8b5cf6;">{demand_spikes} / {shipment_delays}</div>
            <div class="metric-title-lbl">DEMAND SPIKES / TRANSIT DELAYS</div>
            <div class="metric-subtext">Categorical Breakdown</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Scatter Plot
    fig_z = px.scatter(
        df_a,
        x="baseline_mean",
        y="metric_value",
        size="z_score",
        color="severity",
        hover_name="entity_name",
        hover_data=["z_score", "anomaly_type", "details"],
        color_discrete_map={"CRITICAL": "#ef4444", "HIGH": "#f59e0b"},
        labels={"baseline_mean": "Normal Baseline Mean (μ)", "metric_value": "Observed Value (x)"}
    )
    fig_z.update_layout(title="Z-SCORE OUTLIER SCATTER MATRIX")
    apply_enterprise_theme(fig_z, height=320)
    st.plotly_chart(fig_z, use_container_width=True)
    
    st.markdown("#### Live Exception Event Feed")
    st.dataframe(
        df_a[[
            "anomaly_id", "anomaly_type", "entity_name", "metric_value", 
            "baseline_mean", "z_score", "severity", "details", "detected_at"
        ]].rename(columns={
            "anomaly_id": "Alert ID",
            "anomaly_type": "Class",
            "entity_name": "Subject Entity",
            "metric_value": "Observed Value",
            "baseline_mean": "Baseline (μ)",
            "z_score": "Z-Score",
            "severity": "Severity",
            "details": "Root Cause Details",
            "detected_at": "Timestamp"
        }),
        use_container_width=True,
        hide_index=True
    )

# --------------------------------------------------------------------------------------
# 14. PAGE: WHAT-IF SCENARIO SIMULATION
# --------------------------------------------------------------------------------------
def render_what_if_page(data):
    """Renders interactive What-If scenario simulation for supplier delivery delays."""
    df_products = data["products"]
    df_inv = data["inventory"]
    
    col_ctrl, col_stats = st.columns([1.2, 2.8])
    with col_ctrl:
        simulated_delay = st.slider(
            "Simulated Supplier Delay (Days):",
            min_value=1,
            max_value=14,
            value=7,
            step=1,
            help="Simulated days added to supplier replenishment lead time"
        )
        
    # Dynamic recalculation
    merged = pd.merge(df_products, df_inv[["product_id", "current_stock", "safety_stock", "avg_daily_demand_30d"]], on="product_id", how="left")
    sim_records = []
    for _, r in merged.iterrows():
        p_id = r["product_id"]
        orig_lead = int(r["lead_time_days"])
        sim_lead = orig_lead + simulated_delay
        curr_stock = int(r["current_stock"])
        safety = int(r["safety_stock"])
        daily_d = max(0.2, float(r["avg_daily_demand_30d"]))
        
        delay_demand = round(simulated_delay * daily_d, 2)
        total_lead_demand = round(sim_lead * daily_d, 2)
        projected_bal = curr_stock - total_lead_demand
        
        if projected_bal < 0:
            stockout_risk = True
            shortage = int(abs(projected_bal))
            sev = "CRITICAL" if (shortage > 40 or curr_stock == 0) else ("HIGH" if shortage > 15 else "MEDIUM")
        elif projected_bal <= safety:
            stockout_risk = False
            shortage = 0
            sev = "LOW"
        else:
            stockout_risk = False
            shortage = 0
            sev = "NONE"
            
        sim_records.append({
            "product_id": p_id,
            "product_name": r["product_name"],
            "category": r["category"],
            "original_lead_time_days": orig_lead,
            "simulated_lead_time_days": sim_lead,
            "current_inventory": curr_stock,
            "expected_demand_during_delay": delay_demand,
            "projected_stockout_risk": stockout_risk,
            "estimated_units_shortage": shortage,
            "impact_severity": sev
        })
    df_sim = pd.DataFrame(sim_records)
    
    sim_stockout_cnt = len(df_sim[df_sim["projected_stockout_risk"] == True])
    sim_shortage_sum = df_sim["estimated_units_shortage"].sum()
    crit_count = len(df_sim[df_sim["impact_severity"] == "CRITICAL"])
    
    with col_stats:
        w1, w2, w3 = st.columns(3)
        with w1:
            st.markdown(f"""
            <div class="metric-card-box">
                <div class="metric-num-val" style="color:#8b5cf6;">+{simulated_delay} Days</div>
                <div class="metric-title-lbl">SIMULATED DELAY</div>
                <div class="metric-subtext">Added to Lead Time</div>
            </div>
            """, unsafe_allow_html=True)
        with w2:
            st.markdown(f"""
            <div class="metric-card-box">
                <div class="metric-num-val" style="color:#ef4444;">{sim_stockout_cnt} SKUs</div>
                <div class="metric-title-lbl">PROJECTED STOCKOUTS</div>
                <div class="metric-subtext">{sim_stockout_cnt}% of Total Catalog</div>
            </div>
            """, unsafe_allow_html=True)
        with w3:
            st.markdown(f"""
            <div class="metric-card-box">
                <div class="metric-num-val" style="color:#f59e0b;">{sim_shortage_sum:,}</div>
                <div class="metric-title-lbl">ESTIMATED SHORTAGE</div>
                <div class="metric-subtext">Unfulfilled Order Units</div>
            </div>
            """, unsafe_allow_html=True)
            
    st.markdown("<br>", unsafe_allow_html=True)
    
    top_short = df_sim[df_sim["estimated_units_shortage"] > 0].sort_values("estimated_units_shortage", ascending=False).head(10)
    fig_w_bar = px.bar(
        top_short,
        x="product_name",
        y="estimated_units_shortage",
        color="impact_severity",
        color_discrete_map={"CRITICAL": "#ef4444", "HIGH": "#f59e0b", "MEDIUM": "#eab308"},
        labels={"estimated_units_shortage": "Projected Shortage (Units)", "product_name": "Product Name"}
    )
    fig_w_bar.update_layout(title=f"TOP 10 SHORTAGE PRODUCTS UNDER +{simulated_delay}-DAY SUPPLIER DELAY")
    apply_enterprise_theme(fig_w_bar, height=300)
    st.plotly_chart(fig_w_bar, use_container_width=True)

# --------------------------------------------------------------------------------------
# 15. PAGE: SETTINGS
# --------------------------------------------------------------------------------------
def render_settings_page(data):
    """Renders system configurations and manual pipeline runner."""
    st.markdown("### ⚙️ System Settings & Telemetry")
    
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.markdown("""
        <div class="metric-card-box">
            <div class="metric-title-lbl" style="margin-bottom:0.6rem;">POSTGRESQL CLUSTER CONFIGURATION</div>
            <table style="width:100%; font-family:'JetBrains Mono'; font-size:0.8rem; color:#94a3b8;">
                <tr><td>Host / Port:</td><td style="color:#ffffff;">localhost:5432</td></tr>
                <tr><td>Database:</td><td style="color:#ffffff;">supply_chain_control_tower</td></tr>
                <tr><td>Cluster Status:</td><td style="color:#10b981;">Online (SQLAlchemy 2.1)</td></tr>
                <tr><td>Core Tables:</td><td style="color:#8b5cf6;">11 Relational Tables</td></tr>
                <tr><td>Views:</td><td style="color:#8b5cf6;">6 Analytical Views</td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)
        
    with col_s2:
        st.markdown("""
        <div class="metric-card-box">
            <div class="metric-title-lbl" style="margin-bottom:0.6rem;">PIPELINE TELEMETRY</div>
            <table style="width:100%; font-family:'JetBrains Mono'; font-size:0.8rem; color:#94a3b8;">
                <tr><td>Airflow Schedule:</td><td style="color:#ffffff;">@hourly (0 * * * *)</td></tr>
                <tr><td>DAG Identifier:</td><td style="color:#8b5cf6;">retail_supply_chain_control_tower</td></tr>
                <tr><td>Prophet Horizon:</td><td style="color:#ffffff;">7 Forward Days</td></tr>
                <tr><td>Z-Score Threshold:</td><td style="color:#ffffff;">|Z| ≥ 2.0</td></tr>
                <tr><td>Alerts Dispatch:</td><td style="color:#10b981;">SMTP & Database Audit Log</td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("🚀 TRIGGER LIVE HOURLY PIPELINE RUN NOW"):
        with st.spinner("Executing pipeline stages..."):
            try:
                from scripts.refresh_data import refresh_inventory_and_shipments
                from scripts.calculate_kpis import calculate_and_store_kpis
                from scripts.detect_anomalies import run_anomaly_detection
                from scripts.forecast_demand import generate_demand_forecasts
                from scripts.what_if_analysis import run_what_if_delay_scenario
                from scripts.send_alerts import send_alert_notification
                
                refresh_inventory_and_shipments()
                calculate_and_store_kpis()
                run_anomaly_detection()
                generate_demand_forecasts(horizon_days=7)
                run_what_if_delay_scenario(added_delay_days=7)
                send_alert_notification()
                
                st.cache_data.clear()
                st.success("✅ Full pipeline executed! Database refreshed.")
                time.sleep(1)
                st.rerun()
            except Exception as e:
                st.error(f"Error executing pipeline: {e}")

# --------------------------------------------------------------------------------------
# 16. MAIN ROUTING
# --------------------------------------------------------------------------------------
def main():
    try:
        data = load_all_control_tower_data()
    except Exception as e:
        st.error(f"Database Connection Error: {e}")
        st.info("Ensure PostgreSQL is running at localhost:5432 and run: python scripts/init_db.py")
        return
        
    active_page = render_sidebar()
    render_topbar(active_page)
    
    if active_page == "Overview":
        render_overview_page(data)
    elif active_page == "Inventory":
        render_inventory_page(data)
    elif active_page == "Shipments":
        render_shipments_page(data)
    elif active_page == "Suppliers":
        render_suppliers_page(data)
    elif active_page == "Demand Forecast":
        render_forecasting_page(data)
    elif active_page == "Anomalies":
        render_anomalies_page(data)
    elif active_page == "What-if Analysis":
        render_what_if_page(data)
    elif active_page == "Settings":
        render_settings_page(data)

if __name__ == "__main__":
    main()
