# Agentic Ad Optimizer

JSON-native, agentic system for planning, generating, and optimizing ad experiments end-to-end.

---

## What it does

Agentic Ad Optimizer is a vertical slice of an “agentic” marketing copilot that can:

- Ingest product + audience context as a **business snapshot**
- Design a structured **A/B/n experiment plan**
- Generate structured **creative variants** (hook, body, headline, CTA)
- **Score** those creatives against a rubric
- Take in experiment **results** (impressions, spend, conversions, revenue, profit, ROAS)
- Recommend **next tests** based on the winning variant

Everything speaks JSON between components, so it can plug into real ad platforms and analytics later.

---

## Who it’s for

This prototype is built for:

- **Performance marketers** running constant creative tests
- **Founders / growth teams** who want a repeatable creative testing loop
- **Builders & hackers** exploring agentic systems around advertising

The goal is to reduce “spreadsheet thrash” and manual copy-pasting between planning docs, ad platforms, and reporting dashboards.

---

## Current vertical slice

Right now the project ships a complete, local, demo-ready loop:

1. **Backend – FastAPI**
   - `POST /experiment-plan` – builds an `ExperimentPlan` from a `BusinessSnapshot`
   - `POST /creative-variants` – generates `CreativeVariant` objects from that plan
   - `POST /score-creatives` – assigns rubric scores (`RubricScore`) to each creative
   - `POST /results` – processes an `ExperimentResult` and returns a `NextTestRecommendation` with a summary + new variants to test

2. **Frontend – React + Vite**
   A 3-step flow that wraps those APIs:

   - **Step 1 – Business snapshot:** small form (product, price, audience, pain point) → calls `/experiment-plan`
   - **Step 2 – Plan & creatives:** shows the experiment plan, generates creatives, and scores them
   - **Step 3 – Results & next moves:** lets you plug in performance data, then calls `/results` to show the winner and recommended next tests

3. **Tests**
   - `backend/tests/test_main.py` covers all major API endpoints and ensures JSON contracts stay consistent.

---

## Tech stack (current)

**Backend**

- Python 3.10+
- FastAPI
- Pydantic models for all API contracts
- Pytest for backend tests

**Frontend**

- React 18
- Vite dev server / bundler
- Fetch-based client (`frontend/src/api.js`) talking to the FastAPI backend

**Docs & design**

- `docs/architecture.md` – system architecture + data flow
- `docs/api-contracts.md` – request/response schemas for all endpoints
- `Agentic_Ad_Optimizer_Plan.md` – original hackathon plan and long-term roadmap

---

## Repo layout

Current monorepo layout:

```text
backend/                  # FastAPI app, agents, schemas, tests
  app/main.py             # API entrypoint & endpoints
  schemas/models.py       # Pydantic models (BusinessSnapshot, ExperimentPlan, etc.)
  tests/test_main.py      # Pytest suite for core endpoints

frontend/                 # React + Vite web UI
  src/App.jsx             # 3-step flow (snapshot → plan → creatives → results)
  src/api.js              # Fetch wrappers for the FastAPI endpoints
  src/styles.css          # Simple, dark UI styling

docs/
  architecture.md         # High-level architecture & modules
  api-contracts.md        # JSON API contracts

Agentic_Ad_Optimizer_Plan.md  # Original project plan & roadmap
README.md                     # You are here
```

---

## How the agentic loop works

The core loop:

1. **Submit a Business Snapshot**
   - JSON describing products, audiences, and (optionally) historical performance.
   - Example fields: product id, name, price, benefits, audience segment, pain points.

2. **Generate an Experiment Plan (`POST /experiment-plan`)**
   - Returns an `ExperimentPlan` with:
     - `experiment_id`
     - `objective` & `hypothesis`
     - `variants[]` (A/B/C with control/test flags and descriptions)
     - `metrics[]` and `sample_size_rules` (min spend, min conversions)

3. **Generate Creatives (`POST /creative-variants`)**
   - Takes the `ExperimentPlan` and returns a `CreativeVariant` per variant:
     - `variant_id`, `hook`, `primary_text`, `headline`, `call_to_action`

4. **Score Creatives (`POST /score-creatives`)**
   - Evaluates each creative with a rubric and returns `RubricScore`:
     - Dimensions like `clarity_of_promise`, `emotional_resonance`, `call_to_action_score`, `channel_fit`, `overall_strength`, plus textual `feedback`.

5. **Process Results & Recommend Next Tests (`POST /results`)**
   - Input: `ExperimentResult` with metrics per variant and a `winner_variant_id`.
   - Output: `NextTestRecommendation` with:
     - `experiment_id`
     - `recommended_variants[]` (new `VariantPlan`s)
     - `summary` explaining why the recommendation was made

The React frontend walks a user through this entire flow interactively.

---

## Running locally

### 1. Backend (FastAPI)

Requirements: Python 3.10+ and `pip`.

```bash
# From repo root
python -m venv .venv

# Activate the venv
#   Windows (PowerShell)
.\.venv\Scripts\Activate.ps1
#   macOS / Linux
# source .venv/bin/activate

pip install -r requirements.txt

uvicorn backend.app.main:app --reload
```

The backend will be available at **http://localhost:8000**  
You can open **http://localhost:8000/docs** for the FastAPI Swagger UI.

### 2. Frontend (React + Vite)

Requirements: Node 18+ and `npm`.

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at **http://localhost:5173**.

> CORS is enabled in `backend/app/main.py` to allow local frontend calls from `localhost:5173`.

### 3. End-to-end manual test

1. Visit `http://localhost:5173`.
2. **Step 1 – Business snapshot**  
   - Use the defaults or enter product/audience info.  
   - Click **“Generate experiment plan”** → you should see an objective, hypothesis, and variants A/B/C.
3. **Step 2 – Plan & creatives**  
   - Click **“Generate creatives”** → cards appear, one per variant.  
   - Click **“Score creatives”** → each card shows a rubric score + feedback.
4. **Step 3 – Results & next moves**  
   - Keep the prefilled numbers or tweak them.  
   - Click **“Get recommendation”** → see a human-readable summary and next-test variants (D/E).

If all three steps work, the vertical slice is healthy.

---

## Running tests

Backend tests (requires the virtual environment and dependencies installed):

```bash
# From repo root, with venv activated
pytest
```

The suite validates:

- Root endpoint returns the welcome message
- `/experiment-plan` returns a valid experiment with multiple variants
- `/creative-variants` returns a creative per plan variant with headlines
- `/score-creatives` returns a score per creative, including `overall_strength`
- `/results` returns a recommendation with `recommended_variants` and a `summary`

---

## API reference

For detailed request/response JSON schemas, see `docs/api-contracts.md`.

Quick overview:

- `GET /` – Health check / welcome message.
- `POST /experiment-plan` – Input: `BusinessSnapshot`. Output: `ExperimentPlan`.
- `POST /creative-variants` – Input: `ExperimentPlan`. Output: `list[CreativeVariant]`.
- `POST /score-creatives` – Input: `list[CreativeVariant]`. Output: `list[RubricScore]`.
- `POST /results` – Input: `ExperimentResult`. Output: `NextTestRecommendation`.

---

## Roadmap & future work

The original project plan lays out a larger vision: full data ingestion, multi-armed bandit or RL-based optimization, cross-channel deployment, and richer creative generation (text, images, motion).

Some next steps:

- Plug into real ad platform APIs (Meta/Google/TikTok) for ingestion and result sync
- Swap heuristic/random logic for proper bandit / Bayesian optimization
- Use real LLMs / diffusion models for creative generation and scoring
- Expand the frontend into a full dashboard with experiment history and approvals

For now, this repo focuses on a **clean, inspectable, demo-ready agentic loop** that can be extended in multiple directions.
