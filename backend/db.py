import os
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def get_connection():
    """Returns a new connection to the database."""
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable is not set.")
    # Use dict_row to return rows as dictionaries instead of tuples
    return psycopg.connect(DATABASE_URL, row_factory=dict_row)

def execute_query(query: str) -> dict:
    """Executes a SQL query safely and returns the results."""
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                # Security: Kill any query taking longer than 5 seconds
                cur.execute("SET statement_timeout = '5s'")
                
                cur.execute(query)
                # Fetch results if it's a SELECT returning rows
                if cur.description:
                    rows = cur.fetchall()
                    return {"success": True, "data": rows}
                return {"success": True, "data": []}
    except Exception as e:
        return {"success": False, "error": str(e)}