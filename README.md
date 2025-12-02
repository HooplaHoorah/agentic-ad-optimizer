# Agentic Ad Optimizer

JSON-native, agentic system for planning, generating, and optimizing ad experiments end-to-end.

## High-level idea

- Ingest product + performance context
- Design smart A/B/n experiments
- Generate and self-critique creatives using a rubric
- Take in results (CSV/API), compute ROAS/profit, and suggest the next tests

## Quickstart

### Backend

```bash
# Create and activate virtual environment
python -m venv .venv

# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Windows (Command Prompt)
.venv\Scripts\activate.bat

# Mac/Linux
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the backend
uvicorn backend.app.main:app --reload
```

Backend runs at: `http://localhost:8000`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at: `http://localhost:5173`.

Then open the frontend in your browser, click through the 3-step flow, and watch the agent generate a plan, creatives, scores, and a recommendation.

## Tech stack

- **Backend**: Python, FastAPI, LangChain, OpenAI
- **Frontend**: React (Vite) for a simple 3-step UI
- **Everything speaks JSON** between agents

## Monorepo layout

- `backend/` – API, agents, schemas
- `frontend/` – React web UI
- `docs/` – architecture, JSON contracts, and roadmap

## API Overview

The frontend is a thin UI layer over the following backend endpoints:

- **POST /experiment-plan** – Generate an experiment plan from business snapshot
- **POST /creative-variants** – Generate creative variants for each variant in the plan
- **POST /score-creatives** – Score creatives using a rubric
- **POST /results** – Process results and get next test recommendation

For detailed API contracts, see [`docs/api-contracts.md`](docs/api-contracts.md).
