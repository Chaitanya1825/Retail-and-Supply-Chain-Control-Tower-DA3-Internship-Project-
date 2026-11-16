"""
Configuration and Environment Settings for Retail & Supply Chain Control Tower.
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine
import psycopg2

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# PostgreSQL Database Configuration
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "supply_chain_control_tower")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

DATABASE_URI = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
POSTGRES_DEFAULT_URI = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/postgres"

# SMTP Alert Configuration
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
ALERT_RECIPIENT_EMAIL = os.getenv("ALERT_RECIPIENT_EMAIL", "control_tower_alerts@example.com")
ENABLE_EMAIL_ALERTS = os.getenv("ENABLE_EMAIL_ALERTS", "false").lower() in ("true", "1", "yes")

# Forecasting & Anomaly Parameters
PROPHET_FORECAST_HORIZON_DAYS = int(os.getenv("PROPHET_FORECAST_HORIZON_DAYS", "7"))
DELAY_SIMULATION_DAYS = int(os.getenv("DELAY_SIMULATION_DAYS", "7"))
Z_SCORE_THRESHOLD = 2.0  # Statistical outlier threshold for demand spikes & shipment delays

def get_engine():
    """Returns SQLAlchemy Engine connected to the target database."""
    return create_engine(DATABASE_URI)

def get_db_connection():
    """Returns raw psycopg2 connection."""
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
