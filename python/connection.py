import os
import pyodbc
from dotenv import load_dotenv

load_dotenv()

def get_connection_string():
    conn_str = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        f"SERVER={os.getenv('DB_SERVER')};"
        f"DATABASE={os.getenv('DB_NAME')};"
        "Trusted_Connection=yes;"
        "TrustServerCertificate=yes;"
    )
    return conn_str