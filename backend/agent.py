import os
import json
from google import genai
from google.genai import types
from tools import get_schema, run_sql

# Automatically picks up GEMINI_API_KEY from .env
client = genai.Client()

# Stretch Goal 6.4: RAG-lite Business Glossary
GLOSSARY = {
    "revenue": "sum of price * quantity across order_items"
}

SYSTEM_PROMPT = f"""You are an expert AI Data Analyst. 
You answer questions about the database by executing SQL queries.
Always adhere to this business glossary: {json.dumps(GLOSSARY)}

Instructions:
1. ALWAYS call `get_schema()` first to understand the database structure before writing any SQL.
2. Formulate a PostgreSQL SELECT query to answer the user's question.
3. Use the `run_sql(query)` tool to execute the query safely. 
4. If `run_sql` returns an error, read the error, CORRECT your SQL, and try again. 
5. Do NOT make up table or column names.
6. Once you have the data, provide a clear, concise natural language answer summarizing the findings.
"""

def process_question(user_question: str):
    # Initialize chat history with the user's question
    messages = [types.Content(role="user", parts=[types.Part.from_text(text=user_question)])]
    
    last_sql_used = None
    last_rows_json = None
    
    # We disable automatic function calling so we can capture the SQL and rows mid-loop
    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        tools=[get_schema, run_sql],
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
        
    )
    
    MAX_TURNS = 8
    for _ in range(MAX_TURNS):
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=messages,
            config=config
        )
        
        if not response.candidates:
            return "Error: No response from model.", last_sql_used, []
            
        model_message = response.candidates[0].content
        messages.append(model_message)
        
        # Check if the model wants to call a tool
        function_calls = [p.function_call for p in model_message.parts if p.function_call]
        
        if function_calls:
            fc = function_calls[0] # Execute the first requested tool
            tool_name = fc.name
            
            if tool_name == "get_schema":
                result_str = get_schema()
            elif tool_name == "run_sql":
                query = fc.args.get("query", "") if fc.args else ""
                last_sql_used = query
                result_str = run_sql(query)
                
                # Save valid rows so we can return them to the frontend
                if "ERROR:" not in result_str and "0 rows" not in result_str:
                    try:
                        last_rows_json = json.loads(result_str)
                    except:
                        pass
            else:
                result_str = f"Unknown function: {tool_name}"
                
            # Feed the tool's result back to Gemini so it can continue
            func_response_part = types.Part.from_function_response(
                name=tool_name,
                response={"result": result_str}
            )
            messages.append(types.Content(role="user", parts=[func_response_part]))
            
        else:
            # If no function calls, Gemini is giving its final text answer
            return response.text, last_sql_used, last_rows_json or []
            
    return "Error: Reached maximum agent loop turns.", last_sql_used, last_rows_json or []

def select_chart_type(question: str, rows: list) -> dict:
    """Uses a secondary LLM call to classify the data for Recharts rendering."""
    if not rows or len(rows) == 0:
        return {"type": "none", "data": []}
        
    prompt = f"""
    Based on the user question: "{question}" and the SQL result data below:
    {json.dumps(rows[:10])}
    
    Determine the best chart type. 
    Types: 'line' (dates/time series), 'bar' (categories vs metrics), 'pie' (parts of a whole), or 'none' (single value).
    Map the JSON keys to 'x_key' (label/category) and 'y_key' (numeric value).
    
    Respond STRICTLY in JSON format:
    {{"type": "bar", "x_key": "product_name", "y_key": "revenue"}}
    """
    try:
        res = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json", temperature=0)
        )
        chart_config = json.loads(res.text)
        chart_type = chart_config.get("type", "none")
        
        if chart_type in ["bar", "line", "pie"]:
            x_key = chart_config.get("x_key")
            y_key = chart_config.get("y_key")
            
            # Format data generically for Recharts
            chart_data = []
            for row in rows:
                if x_key in row and y_key in row:
                    chart_data.append({"name": str(row[x_key]), "value": float(row[y_key])})
            return {"type": chart_type, "data": chart_data}
    except Exception as e:
        print("Chart mapping error:", e)
        
    return {"type": "none", "data": []}