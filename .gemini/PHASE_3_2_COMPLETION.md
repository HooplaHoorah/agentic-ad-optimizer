# Phase 3.2 Implementation Summary - Reliability & Guardrails

## Status: COMPLETE

### 1. Backend Online Indicator (Reliability Preflight)
- **Backend**: Added `GET /health` endpoint returning `status`, `mode` (live/mock), and `fibo_enabled`.
- **Frontend**: 
    - Added `checkHealth` API function.
    - Implemented persistent status badge in header:
        - `⏳ Checking...`
        - `✅ Online (LIVE/MOCKED)`
        - `❌ Offline` with Retry button.
    - **Circuit Breaker**: Disabled primary action buttons (Generate Plan, Generate Creatives, Score, etc.) when backend is offline.
    - **Retry Logic**: Added global retry mechanism for failed requests.

### 2. Compliance & Brand Guardrails (Enterprise Readiness)
- **Data Model**:
    - Added `Guardrails` Pydantic model (`brand_voice`, `avoid_words`, `required_terms`, `disclaimer`, etc.).
    - Updated `BusinessSnapshot`, `ExperimentPlan`, and `CreativeVariant` to carry guardrails.
- **Backend Logic**:
    - `/experiment-plan`: Pass guardrails from snapshot to plan.
    - `/creative-variants`: 
        - Inject disclaimer into `primary_text`.
        - Validate copy against `avoid_words` and `required_terms`.
        - Generate `guardrails_report` (Pass/Needs Fix + Issues list).
- **Frontend UI**:
    - **Step 1**: Added collapsible "Compliance & Brand Guardrails" section with fields for Voice, Avoid Words, Required Terms, Disclaimer.
    - **State**: `formValues` now includes guardrails with smart defaults per template.
    - **Step 2**: Creative Cards now display a Guardrails Badge:
        - `✅ Guardrails: Pass`
        - `⚠️ Guardrails: Needs fix` (with list of issues).
- **Export**: Guardrails settings and per-variant reports are automatically included in the JSON export bundle.

### 3. Verification & Evidence
- **Browser Check**: Verified "Offline" badge appears when backend is down.
- **Evidence Script**: Updated `backend/scripts/generate_demo_outputs.py` to include guardrails in the demo usage pattern, ensuring `guardrails` field is present in generated `01_experiment_plan_request.json`.

### 4. Code Changes
- `backend/app/main.py`: Health endpoint, Guardrails logic.
- `backend/schemas/models.py`: Guardrails models.
- `frontend/src/api.js`: `checkHealth` function.
- `frontend/src/App.jsx`: UI integration, State management, Button disabling.
- `frontend/src/styles.css`: Badge styling.
- `backend/scripts/generate_demo_outputs.py`: Added advanced exploration step.

### 5. Optional: Extra Exploration Axes
- **Frontend**: Added "Advanced Axis Config" toggle in the Creative Card.
- **Features**: User can now select from `shot_type`, `camera_angle`, `subject_distance`, etc.
- **Visual Grid**: Updated grid popout to dynamically label the axes being explored.
- **Evidence**: Demo script now generates a second grid exploring `shot_type` and `camera_angle`.

## Ready for Demo / Evidence Generation
Run `python backend/scripts/generate_demo_outputs.py` to create the evidence pack.
