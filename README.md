# Agentic Ad Optimizer

JSON-native, agentic system for planning, generating, and optimizing ad experiments end-to-end.

## High-level idea

- Ingest product + performance context
- Design smart A/B/n experiments
- Generate and self-critique creatives using a rubric
- Take in results (CSV/API), compute ROAS/profit, and suggest the next tests

## Tech stack (planned)

- Backend: Python, FastAPI, LangChain, OpenAI / Fal.ai
- Frontend: React (or Next.js) for a simple 3–4 screen UI
- Everything speaks JSON between agents

## Monorepo layout

- `backend/` – API, agents, schemas
- `frontend/` – web UI
- `docs/` – architecture, JSON contracts, and roadmap
