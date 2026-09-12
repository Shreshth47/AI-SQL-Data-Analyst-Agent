import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agent import process_question, select_chart_type

app = FastAPI()

# Allow the React frontend to communicate with this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    question: str

@app.post("/ask")
def ask_question(req: QueryRequest):
    print(f"Processing question: {req.question}")
    
    # 1. Run the agent loop
    answer, sql_used, rows = process_question(req.question)
    
    # 2. Pick the chart format
    chart = {"type": "none", "data": []}
    if rows:
        chart = select_chart_type(req.question, rows)
        
    return {
        "answer": answer,
        "sql": sql_used,
        "rows": rows,
        "chart": chart
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)