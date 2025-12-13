# instructions8.md — Phase 3.2: Reliability Preflight + Compliance/Brand Guardrails (+ optional extra Explore axes)

Owner: Antigravity  
Scope: **Do NOT** work on deployment or Devpost submission in this phase.  
Goal: two “enterprise judge bump” improvements that are demo-visible and low-risk:
1) **Backend Online ✅ indicator** (ping `/health`) to prevent “Failed to fetch” moments.
2) **Compliance / Brand Guardrails** (lightweight, visible, exportable).
Optional (if time): add **1–2 extra exploration axes** so the grid feels like real search.

---

## A) Backend Online ✅ indicator (Preflight)

### A1) Backend: add/confirm `GET /health`
Implement (or standardize) a health endpoint:

**Route**
- `GET /health`

**Response (example)**
```json
{
  "status": "ok",
  "mode": "live",
  "fibo_enabled": true
}
```

Rules:
- `mode = "live"` when `FIBO_API_KEY` is present; otherwise `"mocked"`.
- Always return 200 quickly.
- No secrets in response.

**Acceptance**
- `curl http://localhost:8000/health` returns 200 within ~100ms.
- Response clearly indicates LIVE vs MOCKED.

### A2) Frontend: persistent badge + Retry + disable-risky actions when offline
Add a small persistent status widget (top-right or near the “Bria FIBO: LIVE” badge):

States:
- ⏳ **Backend: Checking…**
- ✅ **Backend: Online** (show LIVE/MOCKED mode)
- ❌ **Backend: Offline** + one-line fix + **Retry** button

Behavior:
- On app load: ping `/health`.
- On any network failure: set Offline and show fix text:
  - “Backend unreachable. Start: `uvicorn backend.app.main:app --reload --port 8000`”
- Provide **Retry** button to re-check `/health` and recover without reload.
- When Offline: disable actions that call backend (Generate plan/creatives/score/explore/regenerate/export) *or* show a modal warning.

Optional: configurable API base URL:
- `VITE_API_BASE_URL` default `http://localhost:8000`

**Acceptance**
- No raw “Failed to fetch” ever appears; error UI is actionable.
- Restarting backend + clicking Retry flips badge to Online and re-enables buttons.

**Report back**
- Screenshot (Online LIVE)
- Screenshot (Offline + fix text + Retry)
- 10–15 sec recording: stop backend → badge offline → restart → Retry → online

---

## B) Compliance / Brand Guardrails (Enterprise bump)

### Why
Makes the app look production/enterprise-ready: safe claims, required disclaimers, brand tone, and platform constraints.

### B1) Frontend: add “Guardrails” section in Step 1 (Business snapshot)
Add a collapsible “Guardrails (optional)” section with small, simple fields:

**Brand**
- Brand voice rules (textarea)
- Words/phrases to avoid (comma-separated)
- Required terms (comma-separated)

**Compliance**
- Required disclaimer (textarea)
- Prohibited claims (textarea or checkboxes)
- Regulated category (dropdown): none / health / finance / alcohol / kids / other

**Platform**
- Target channel (dropdown): Meta / Google / TikTok / LinkedIn

Template defaults:
- Each campaign template (SaaS/DTC/Local) pre-fills sensible guardrails.
- Switching templates should not wipe user edits unless user confirms.

**Acceptance**
- Guardrails persist through steps and exports.
- Template switching is idempotent (no broken state).

### B2) Backend: incorporate guardrails into plan + copy + image spec prompt
Wherever we generate:
- Experiment plan + hypothesis
- Ad copy fields (hook / primary / headline / CTA)
- FIBO spec prompt (and/or any supporting prompt fields)

Inject guardrails explicitly:
- Must include disclaimer (if provided)
- Avoid list must not appear
- Required terms appear (if provided)
- No prohibited claims
- Platform-specific tone/length constraints (light)

**Acceptance**
- If user provides a required disclaimer, it appears in relevant text output.
- Avoid list words do not appear in generated copy.

### B3) Add a deterministic “Guardrail Check” (lint, not moderation)
Create a simple validator that checks text fields per variant:

Checks:
- Disclaimer present (if provided)
- Avoid list absent
- Required terms present (if provided)
- Optional: length limits based on platform

UI:
- Per creative variant, show badge:
  - ✅ Guardrails: Pass
  - ⚠️ Guardrails: Needs fix
- If Needs fix: show the failing rule(s).
- (Optional) Add a “Fix copy” button that regenerates only text fields with guardrails applied.

**Acceptance**
- Validator is deterministic and fast.
- Results are included in export (e.g., `guardrails_report.json`).

### B4) Export + evidence integration
Ensure existing **Export** includes:
- Guardrails inputs
- Per-variant guardrail results
- Any auto-fixes performed

If evidence pack generator exists (`generate_demo_outputs.py`):
- Include at least one run with guardrails enabled (disclaimer + avoid list), so it shows up in `demo_outputs`.

**Report back**
- Screenshot: Guardrails UI section filled
- Screenshot: a variant showing Guardrails Pass/Needs fix
- Export bundle listing containing guardrails JSON/report
- If using evidence pack: tree listing showing guardrails artifacts

---

## C) Optional: Add 1–2 extra exploration axes (make grid feel like real search)
If time allows, extend the existing Explore grid beyond lighting/palette/background with 1–2 more **FIBO-relevant** axes such as:

Candidates (choose what your schema supports):
- `shot_type` (e.g., product_only vs lifestyle)
- `camera_angle` (eye_level vs high_angle)
- `composition` or crop hint (if supported)
- `subject_distance` (close vs medium)

Implementation:
- Keep default grid at 8 for speed, but add an “Advanced” toggle that lets the user include extra axis choices (still bounded).
- Ensure each tile labels the axis combo (“warm + pastel + lifestyle”).

**Acceptance**
- Grid still renders quickly.
- JSON inspector shows axis values clearly and changed fields reflect only axis keys.

**Report back**
- Screenshot: grid showing new axis label(s)
- One tile expanded showing JSON and changed keys

---

## Definition of done (Phase 3.2)
- [ ] `/health` endpoint exists and is used by UI badge
- [ ] UI shows Online/Offline with Retry and no raw “Failed to fetch”
- [ ] Guardrails UI exists, persists, affects generation, and validates deterministically
- [ ] Export includes guardrails inputs + per-variant guardrail report
- [ ] (Optional) Extra exploration axes available and demo-visible
