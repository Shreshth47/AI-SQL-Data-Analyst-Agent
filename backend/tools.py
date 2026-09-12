from db import execute_query
from validator import validate_sql

# Cache the schema in memory so we don't query the DB on every LLM loop
_SCHEMA_CACHE = None

def get_schema() -> str:
    """Returns the database schema for the LLM to understand tables and columns."""
    global _SCHEMA_CACHE
    if _SCHEMA_CACHE:
        return _SCHEMA_CACHE

    query = """
    SELECT table_name, column_name, data_type 
    FROM information_schema.columns 
    WHERE table_schema = 'public'
    ORDER BY table_name;
    """
    
    result = execute_query(query)
    if not result["success"]:
        return "Error fetching schema: " + result["error"]
        
    # Group columns by table
    schema_dict = {}
    for row in result["data"]:
        t_name = row["table_name"]
        c_name = row["column_name"]
        d_type = row["data_type"]
        
        if t_name not in schema_dict:
            schema_dict[t_name] = []
        schema_dict[t_name].append(f"{c_name} ({d_type})")
        
    # Format into a compact string: "Table: orders | Columns: id (integer), date (date)"
    schema_lines = []
    for table, cols in schema_dict.items():
        schema_lines.append(f"Table: {table} | Columns: {', '.join(cols)}")
        
    _SCHEMA_CACHE = "\n".join(schema_lines)
    return _SCHEMA_CACHE

def run_sql(query: str) -> str:
    """Validates and executes a SQL query, returning rows or error messages."""
    # 1. Validate first
    validation = validate_sql(query)
    if not validation["is_valid"]:
        return f"VALIDATION ERROR: {validation['error']}\nPlease fix the SQL and try again."
        
    # 2. Execute
    result = execute_query(query)
    if not result["success"]:
        return f"EXECUTION ERROR: {result['error']}\nPlease fix the SQL and try again."
        
    # Return stringified data for the LLM to read
    rows = result["data"]
    if not rows:
        return "Query executed successfully but returned 0 rows."
        
    import json
    # Truncate to first 50 rows just in case, to save LLM tokens
    return json.dumps(rows[:50], default=str)