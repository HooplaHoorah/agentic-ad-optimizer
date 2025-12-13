# Agentic Ad Optimizer

JSON-native, agentic system for planning, generating, and optimizing ad experiments end-to-end.

---

## What it does

Agentic Ad Optimizer is a vertical slice of an "agentic" marketing copilot that can:

- Ingest product + audience context as a **business snapshot**
- Design a structured **A/B/n experiment plan**
- Generate structured **creative variants** (hook, body, headline, CTA)
- **Score** those creatives against a rubric
- Take in experiment **results** (impressions, spend, conversions, revenue, profit, ROAS)
- Recommend **next tests** based on the winning variant

Everything speaks JSON between components, so it can plug into real ad platforms and analytics later.

---

## Who it's for

This prototype is built for:

- **Performance marketers** running constant creative tests
- **Founders / growth teams** who want a repeatable creative testing loop
- **Builders & hackers** exploring agentic systems around advertising

The goal is to reduce "spreadsheet thrash" and manual copy-pasting between planning docs, ad platforms, and reporting dashboards.

---

## Quickstart (New!)

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


## Judge Quickstart (2-3 Commands to Success) ️

### Prerequisites
- **Python 3.10+**
- **Node.js 18+**
- **Git**
- (Optional) **Bria FIBO API Key** for production image generation

### Step 1: Backend Setup

```bash
# Clone the repo (if you haven't)
git clone <repo-url>
cd agentic-ad-optimizer

# Create and activate virtual environment
python -m venv .venv

# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Windows (Command Prompt)
.venv\Scripts\activate.bat

# macOS / Linux
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### Set FIBO_API_KEY (Production Mode)

**Important:** The app works with or without a FIBO API key, but setting it enables **LIVE** image generation.

**Windows (PowerShell):**
```powershell
$env:FIBO_API_KEY="your_bria_api_key_here"
```

**Windows (Command Prompt):**
```cmd
set FIBO_API_KEY=your_bria_api_key_here
```

**macOS / Linux:**
```bash
export FIBO_API_KEY="your_bria_api_key_here"
```

**Persistent Setup (Optional):**
Create a `.env` file in the root directory:
```
FIBO_API_KEY=your_bria_api_key_here
FIBO_API_URL=https://engine.prod.bria-api.com/v2/image/generate
```

#### Run the Backend

```bash
# From repo root (with venv activated)
uvicorn backend.app.main:app --reload --port 8000
```

Backend will be available at: **http://localhost:8000**  
API docs (Swagger): **http://localhost:8000/docs**

### Step 2: Frontend Setup

**Open a new terminal** and run:

```bash
cd frontend
npm install
npm run dev
```

Frontend will be available at: **http://localhost:5173**

### Step 3: Run the Demo

1. Open **http://localhost:5173** in your browser
2. Select a **Campaign Template** (e.g., "SaaS - FlowPilot AI Scheduler")
3. Click **"Generate experiment plan"**
4. Click **"Generate creatives"** → wait for images to load
5. Try a preset: click **"Lifestyle"** on Variant B, then **"Regenerate image"**
6. Click **"Score creatives"**
7. Navigate to **Results**, click **"Get recommendation"**
8. See winner card with FIBO specs + score breakdown
9. Click **"📦 Export All Artifacts"** to download results

## Success Criteria (What to Look For)

### ✅ LIVE Mode (with FIBO_API_KEY set)
- Creative cards show **"Bria FIBO: LIVE ✅"** badge
- Image URLs point to Bria CDN (not `placehold.co`)
- Regeneration creates visibly different images based on presets
- Backend logs show: `regenerate-image creative_id=X status=fibo`

### ⚠️ Mock Mode (without FIBO_API_KEY)
- Creative cards show **"Mock ⚠️"** badge
- Image URLs are from `placehold.co`
- Regeneration still works; specs update but images stay placeholder
- Backend logs show: `regenerate-image creative_id=X status=mocked`
- **This is expected and functional!** The app demonstrates agentic logic even in mock mode

### 🏆 Agentic Loop is Visible
- Winner creative card shows:
  - Winner image
  - Key FIBO parameters (shot_type, lighting_style, color_palette, etc.)
  - Score breakdown by dimension (Clarity, Emotional, Credibility, etc.)
- Recommendation summary references visual parameters
- Export downloads JSON with full experiment data

## Troubleshooting

### Issue: Mock Badge Instead of LIVE
**Cause:** FIBO_API_KEY not set or backend not restarted  
**Fix:**
1. Set the environment variable in your current terminal session
2. Restart the backend: `uvicorn backend.app.main:app --reload --port 8000`
3. Refresh the frontend and generate creatives again

### Issue: 401/403 Error from FIBO
**Cause:** Invalid or expired API key  
**Fix:**  
1. Verify your key is correct (check for extra spaces)
2. Contact Bria support if key permissions are insufficient

### Issue: Placeholder URLs Even with Key Set
**Cause:** Bria API unreachable or network issue  
**Fix:**
1. Check backend logs for error messages
2. Verify `FIBO_API_URL` is correct
3. Test connection: `curl https://engine.prod.bria-api.com/v2/image/generate`

### Issue: Port Conflict (8000 or 5173 already in use)
**Fix:**
- **Backend:** `uvicorn backend.app.main:app --reload --port 8001`  
  Then update `frontend/src/api.js` to point to `http://localhost:8001`
- **Frontend:** Edit `frontend/vite.config.js` to use a different port

### Issue: Frontend Can't Reach Backend
**Cause:** CORS or port mismatch  
**Fix:**
1. Verify backend is running on port 8000
2. Check `frontend/src/api.js` has `API_BASE = "http://localhost:8000"`
3. Open browser DevTools → Network tab to see failed requests

### Issue: Export Button Doesn't Download Anything
**Cause:** Browser popup blocker or no recommendation data  
**Fix:**
1. Make sure you've clicked "Get recommendation" first
2. Check browser console for errors
3. Allow popups/downloads for localhost

Then open the frontend in your browser, click through the 3-step flow, and watch the agent generate a plan, creatives, scores, and a recommendation.

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

## Tech stack

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
- `DEMO_SCRIPT.md` – 2-3 minute demo walkthrough guide

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
DEMO_SCRIPT.md                 # Demo walkthrough guide
README.md                      # You are here
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



### Optional: Enable FIBO image generation

By default the backend returns a deterministic placeholder image for each creative. To call Bria's FIBO image generation API instead, set the following environment variables before starting the backend:

```bash
export FIBO_API_KEY=your_bria_api_key
export FIBO_API_URL=https://engine.prod.bria-api.com/v2/image/generate
...
uvicorn backend.app.main:app --reload


When `FIBO_API_KEY` is not set, the backend will gracefully fall back to the placeholder image. See `backend/app/fibo_client.py` for more details.
icorn backend.app.main:app --reload


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
   - Use the defaults (Math Wars Meta DIY Kit) or enter product/audience info.  
   - Click **"Generate experiment plan"** → you should see an objective, hypothesis, and variants A/B/C.
3. **Step 2 – Plan & creatives**  
   - Click **"Generate creatives"** → cards appear, one per variant.  
   - Click **"Score creatives"** → each card shows a rubric score + feedback.
4. **Step 3 – Results & next moves**  
   - Keep the prefilled numbers or tweak them.  
   - Click **"Get recommendation"** → see a human-readable summary and next-test variants (D/E).

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

- `POST /regenerate-image` - Input: `RegenerateRequest` containing a `creative_id` and a patch for the existing `FiboImageSpec`. Output: `CreativeVariant` with an updated `image_url`, merged `fibo_spec`, and `image_status`.

---

## Roadmap & future work

The original project plan lays out a larger vision: full data ingestion, multi-armed bandit or RL-based optimization, cross-channel deployment, and richer creative generation (text, images, motion).

Some next steps:

- Plug into real ad platform APIs (Meta/Google/TikTok) for ingestion and result sync
- Swap heuristic/random logic for proper bandit / Bayesian optimization
- Use real LLMs / diffusion models for creative generation and scoring
- Expand the frontend into a full dashboard with experiment history and approvals
- - Surface the FIBO-generated images in the React UI and allow users to edit image parameters or regenerate images via the `/regenerate-image` endpoint.


For now, this repo focuses on a **clean, inspectable, demo-ready agentic loop** that can be extended in multiple directions.
