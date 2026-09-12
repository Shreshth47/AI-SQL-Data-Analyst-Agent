# AI SQL / Data Analyst Agent

An enterprise-ready, autonomous AI Data Analyst that bridges the gap between natural language questions and relational databases. Instead of relying on a fragile one-shot prompt pipeline, this agent utilizes native LLM tool calling, AST-based SQL query validation, multi-layer security sandboxing, self-healing query loops, and automated chart classification to deliver trustworthy data insights.

---

## Architecture Overview

```
┌────────────────────────────────────────────────────────────────────────┐
│                        FRONTEND (React + Vite)                         │
│   Port: 5173 | UI Components: ChatWindow, ResultTable, ChartView       │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ HTTP POST /ask
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                       BACKEND (FastAPI / Python)                       │
│   Port: 8000                                                           │
│                                                                        │
│   ┌────────────────────────────────────────────────────────────────┐   │
│   │                         Agent Loop                             │   │
│   │  1. Prompt + Tool definitions sent to LLM                      │   │
│   │  2. Model requests tool call (get_schema / run_sql)            │   │
│   │  3. Loop repeats until model outputs final text response       │   │
│   └───────────────▲───────────────────────────────┬────────────────┘   │
│                   │                               │                    │
│      Tool calls & │                               │ Function calls     │
│      Tool responses                               ▼                    │
│                   │                   ┌────────────────────────────┐   │
│                   │                   │     AST SQL Validator      │   │
│                   │                   │ (sqlglot checks SELECT &   │   │
│                   │                   │         LIMIT)             │   │
│                   │                   └─────────────┬──────────────┘   │
│                   │                                 │                  │
│                   ▼                                 ▼                  │
└───────┬───────────────────────┬─────────────────────┼──────────────────┘
        │                       │                     │
        │ API Request (HTTPS)   │ SQL Query           │
        ▼                       ▼ (psycopg / TCP)     ▼
┌───────────────────────┐   ┌────────────────────────────────────────────┐
│      CLOUD LLM        │   │             DOCKER CONTAINER               │
│   Groq API Server     │   │   Host Port: 5433 ──► Container Port: 5432 │
│                       │   │                                            │
│ Model:                │   │   PostgreSQL 15                            │
│ openai/gpt-oss-20b    │   │   ├── Database: northwind                  │
│ Tool-calling engine   │   │   └── Role: agent_readonly                 │
└───────────────────────┘   └────────────────────────────────────────────┘
```

---

## Key Features

* **Autonomous Agent Loop**: The agent inspects database tables, writes SQL, assesses query errors, and re-evaluates its approach dynamically using function calling.
* **Abstract Syntax Tree (AST) Validation**: Powered by `sqlglot`, all generated SQL is parsed into syntax trees before execution. Non-`SELECT` statements, stacked queries (SQL injections), and unbounded table dumps are rejected prior to hitting the database.
* **Self-Healing SQL Execution**: When the validator flags an issue or the database throws a runtime syntax error, the raw error output is fed back into the agent loop so the model can self-correct and retry.
* **Multi-Layer Defense in Depth**:
  * **Role-Based Isolation**: Connects to the database through a strictly provisioned `agent_readonly` user role. Destructive mutations (`DROP`, `DELETE`, `INSERT`, `UPDATE`, `ALTER`) trigger hard engine-level permission rejections.
  * **Execution Timeout Safeguard**: Every query session enforces a strict statement timeout (`SET statement_timeout = '5s'`) to prevent denial-of-service locks from runaway joins.
  * **Turn Cap Safety**: The backend enforces a maximum turn limit (`MAX_TURNS = 8`) to eliminate runaway recursion and API token exhaustion.
* **Automated Visualization Engine**: Evaluates query results against the user's intent to automatically classify and structure data for Line Charts, Bar Charts, and Pie Charts using Recharts.
* **Domain Knowledge Grounding**: Injects a customizable business glossary into the agent's system prompt (e.g., standard formulas for calculating revenue, handling discounts, and filtering void transactions).
* **Auditable & Polished UI**: Collapsible drawer showing the exact generated SQL query, dynamic data tables for raw verification, and typography with full Markdown and LaTeX math rendering support.

---

## Tech Stack

### Backend
* **Python 3.11+**
* **FastAPI**: Asynchronous high-performance REST API routing.
* **Groq SDK**: Ultra-low-latency model inference powering tool calling.
* **SQLGlot**: SQL parsing, transpilation, and AST-level safety evaluation.
* **Psycopg 3**: Modern PostgreSQL database adapter with dictionary row mapping.
* **Pydantic**: Structured request validation and schema definition.

### Frontend
* **React 18 (Vite)**
* **Tailwind CSS v4**: Utility-first styling with `@tailwindcss/typography`.
* **Recharts**: Responsive SVG charts (Bar, Line, Pie).
* **ReactMarkdown & KaTeX**: Markdown rendering with LaTeX math notation support (`remark-gfm`, `remark-math`, `rehype-katex`).
* **Lucide React**: Clean UI iconography.
* **Axios**: Asynchronous client-server communication.

### Database & DevOps
* **Docker & Docker Compose**: Containerized PostgreSQL 15 environment.
* **PostgreSQL (Northwind Schema)**: Relational analytical test bed.

---

## Project Structure

```text
ai-sql-agent/
├── backend/
│   ├── agent.py            # Agentic orchestration, tool calling & chart classification
│   ├── db.py               # Connection management, read-only pooling & timeouts
│   ├── main.py             # FastAPI application & /ask endpoint definition
│   ├── tools.py            # get_schema and run_sql tool implementations
│   ├── validator.py        # SQLGlot AST query inspection & safety gates
│   ├── requirements.txt    # Python backend dependencies
│   └── .env                # Environment secrets (GROQ_API_KEY, DATABASE_URL)
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChartView.jsx    # Dynamic Recharts renderer
│   │   │   ├── ChatWindow.jsx   # Interactive message thread & input controls
│   │   │   └── ResultTable.jsx  # Formatted tabular result inspector
│   │   ├── api.js               # Axios client instance
│   │   ├── App.jsx              # Root application layout
│   │   ├── index.css            # Tailwind styles & typography plugin
│   │   └── main.jsx             # React DOM entry point
│   ├── package.json
│   └── vite.config.js
└── db/
    ├── docker-compose.yml       # PostgreSQL container configuration (Port 5433:5432)
    └── init.sql                 # Schema initialization & agent_readonly role creation
```

---

## Getting Started

### Prerequisites
* [Docker Desktop](https://www.docker.com/products/docker-desktop/) (running with WSL2 backend on Windows)
* [Python 3.11+](https://www.python.org/downloads/)
* [Node.js 18+](https://nodejs.org/)
* A free [Groq API Key](https://console.groq.com)

---

### Step 1: Clone and Set Up the Database

1. Clone this repository and move into the database folder:
   ```bash
   git clone https://github.com/Shreshth47/AI-SQL-Data-Analyst-Agent
   cd AI-SQL-Data-Analyst-Agent
   ```

2. Start the PostgreSQL Docker container:
   ```bash
   docker-compose up -d
   ```
   *Note: Port `5433` on the host machine maps to port `5432` in the container to avoid colliding with any locally installed PostgreSQL instance.*

---

### Step 2: Configure and Run the Backend

1. Navigate to the `backend` directory:
   ```bash
   cd ../backend
   ```

2. Create and activate a Python virtual environment:
   ```bash
   # On macOS/Linux:
   python3 -m venv venv
   source venv/bin/activate

   # On Windows:
   python -m venv venv
   venv\Scripts\activate
   ```

3. Install required Python packages:
   ```bash
   pip install fastapi uvicorn groq sqlglot "psycopg[binary]" python-dotenv pydantic
   ```

4. Create a `.env` file in the `backend/` directory:
   ```env
   GROQ_API_KEY=gsk_your_groq_api_key_here
   DATABASE_URL=postgresql://agent_readonly:readonly_password@localhost:5433/northwind
   ```

5. Launch the FastAPI server:
   ```bash
   python main.py
   ```
   *The API will start running at `http://localhost:8000`.*

---

### Step 3: Configure and Run the Frontend

1. Open a new terminal and move into the `frontend` folder:
   ```bash
   cd ../frontend
   ```

2. Install client dependencies:
   ```bash
   npm install
   ```

3. Start the Vite development server:
   ```bash
   npm run dev
   ```

4. Open your browser and navigate to `http://localhost:5173`.

---

## Verified Demo Questions

| Intent | Sample Prompt | Expected Visualization | Guardrail Verified |
|---|---|---|---|
| **Aggregated Ranking** | *"Which 5 products generated the most revenue?"* | Bar Chart | Validated multi-table `JOIN`, `GROUP BY`, and `ORDER BY`. |
| **Category Breakdown** | *"Show total revenue grouped by product category."* | Bar Chart | Business glossary lookup applied. |
| **Chronological Trend** | *"Show the monthly revenue trend."* | Line Chart | Date truncation / grouping aggregation. |
| **Market Share** | *"What is the revenue distribution across categories?"* | Pie Chart | Part-of-whole auto-classification. |
| **Security Audit** | *"DROP TABLE products;"* | N/A (Blocked) | AST validator blocks non-`SELECT` statements before execution. |

---

## Security Model Details

1. **AST Parsing via SQLGlot**: Incoming SQL strings are parsed into an Abstract Syntax Tree. Multiple expressions in one statement (e.g., `; DROP TABLE`) are caught and rejected immediately.
2. **Least Privilege ACLs**: The `agent_readonly` PostgreSQL role is granted only `USAGE` on the `public` schema and `SELECT` permissions on tables. Write operations are blocked at the engine layer.
3. **Execution Guard**: `SET statement_timeout = '5s'` is executed on every cursor session, terminating long-running Cartesian queries automatically.
4. **Boundary Isolation**: User inputs are sent to the LLM purely as message content and are never directly interpolated into SQL strings.
