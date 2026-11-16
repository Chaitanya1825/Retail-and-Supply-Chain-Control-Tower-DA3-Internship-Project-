"""
Database Initialization Script for Retail & Supply Chain Control Tower.
Creates database, schema tables, and analytical views in PostgreSQL.
"""
import sys
from pathlib import Path
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Add root folder to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from config.settings import (
    DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
)

def create_database_if_not_exists():
    """Connects to default postgres DB and creates target DB if absent."""
    print(f"[*] Checking PostgreSQL connection at {DB_HOST}:{DB_PORT} as {DB_USER}...")
    try:
        conn = psycopg2.connect(
            dbname="postgres",
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            connect_timeout=5
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        
        cur.execute(f"SELECT 1 FROM pg_database WHERE datname = '{DB_NAME}'")
        exists = cur.fetchone()
        if not exists:
            print(f"[+] Creating database '{DB_NAME}'...")
            cur.execute(f"CREATE DATABASE {DB_NAME};")
            print(f"[✓] Database '{DB_NAME}' created successfully.")
        else:
            print(f"[✓] Database '{DB_NAME}' already exists.")
            
        cur.close()
        conn.close()
    except Exception as e:
        print(f"[!] Error checking/creating database: {e}")
        raise

def apply_sql_file(conn, sql_path: Path):
    """Executes all statements in a SQL file."""
    print(f"[*] Executing SQL script: {sql_path.name}...")
    with open(sql_path, "r", encoding="utf-8") as f:
        sql_content = f.read()
        
    with conn.cursor() as cur:
        cur.execute(sql_content)
    conn.commit()
    print(f"[✓] Successfully executed {sql_path.name}")

def init_schema():
    """Initializes tables and views."""
    create_database_if_not_exists()
    
    print(f"[*] Connecting to '{DB_NAME}' to apply schema and views...")
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    
    schema_file = ROOT_DIR / "sql" / "schema.sql"
    views_file = ROOT_DIR / "sql" / "views.sql"
    
    apply_sql_file(conn, schema_file)
    apply_sql_file(conn, views_file)
    
    # Verify tables
    with conn.cursor() as cur:
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """)
        tables = [row[0] for row in cur.fetchall()]
        print(f"[✓] Initialized {len(tables)} tables: {', '.join(tables)}")
        
        cur.execute("""
            SELECT table_name 
            FROM information_schema.views 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        views = [row[0] for row in cur.fetchall()]
        print(f"[✓] Initialized {len(views)} views: {', '.join(views)}")
        
    conn.close()
    print("[✓] Database initialization complete.")

if __name__ == "__main__":
    init_schema()

