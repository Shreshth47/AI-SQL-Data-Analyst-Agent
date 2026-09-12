import sqlglot
from sqlglot import exp

def validate_sql(query: str) -> dict:
    """
    Parses and validates the SQL query.
    Returns {"is_valid": True} or {"is_valid": False, "error": "reason"}
    """
    try:
        # 1. Parse the query
        parsed_statements = sqlglot.parse(query, read="postgres")
        
        # 2. Reject empty queries
        if not parsed_statements or parsed_statements[0] is None:
            return {"is_valid": False, "error": "Query is empty or invalid."}
        
        # 3. Reject multiple statements (Injection protection)
        if len(parsed_statements) > 1:
            return {"is_valid": False, "error": "Multiple SQL statements are not allowed."}
        
        ast = parsed_statements[0]
        
        # 4. Must be a SELECT statement
        if not isinstance(ast, exp.Select):
            return {"is_valid": False, "error": "Only SELECT statements are allowed."}

        # 5. Missing LIMIT check for safety (Basic heuristic)
        # If there is no LIMIT and no GROUP BY, it might dump too much data.
        has_limit = ast.args.get("limit") is not None
        has_group = ast.args.get("group") is not None
        has_agg = any(isinstance(node, (exp.Sum, exp.Count, exp.Avg, exp.Max, exp.Min)) for node in ast.find_all(exp.Expression))
        
        if not has_limit and not has_group and not has_agg:
            return {"is_valid": False, "error": "Query must include a LIMIT clause to prevent massive data dumps."}
            
        return {"is_valid": True}

    except sqlglot.errors.ParseError as e:
        return {"is_valid": False, "error": f"SQL Syntax Error: {str(e)}"}
    except Exception as e:
        return {"is_valid": False, "error": f"Validation Error: {str(e)}"}