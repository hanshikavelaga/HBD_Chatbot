# db.py — MySQL connection helper (uses environment variables from .env)
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    """Get a single MySQL connection to the company database (genuineh_dashboard)."""
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "172.105.48.130"),
        port=int(os.getenv("MYSQL_PORT", 3306)),
        user=os.getenv("MYSQL_USER", "genuineh_dashboard"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE", "genuineh_dashboard"),
        charset="utf8mb4",
        collation="utf8mb4_general_ci",
        autocommit=True,
    )