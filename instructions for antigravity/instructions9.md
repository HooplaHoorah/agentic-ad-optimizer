# instructions9.md — P0++ “top prize contender” polish (non-DevPost)

Context
- P0 + Phase 3.1 items are done (Spec Inspector, Lock Lighting regen, exploration grids, export, evidence pack generator, online badge, friendly errors).
- We’re *not* doing deployment or DevPost packaging in this sprint.

Goal
Make the demo feel “enterprise judge ready” by ensuring:
1) **Compliance/Brand Guardrails** are not just *detected* but can be *satisfied* (auto-fix / enforcement).
2) No user ever sees raw browser/network errors like **“Failed to fetch”**.
3) Score scale is consistent + clearly labeled (avoid confusion).

---

## Task A — Guardrails enforcement + “Auto-fix copy” (highest leverage)

### A1) Ensure creatives can PASS guardrails by default
When an ExperimentPlan includes guardrails (required_terms / avoid_words / disclaimers), make sure **generated copy includes them**.

**Minimum implementation (fast, demo-safe):**
- Add a helper in backend creative generation:
  - If `required_terms` exist, ensure they appear at least once across `{hook, primary_text, headline}`.
    - Easiest: append to `primary_text` (or a dedicated `disclaimer` field) like:
      - `Dermatologist-tested. Reef-safe.` (joined from required terms)
  - If `disclaimer` exists, append it as a final sentence in `primary_text` (or as a dedicated `disclaimer` field in the model + UI).
  - If `avoid_words` exist, run a simple check and regenerate or sanitize (string replace) if any appear.

**Acceptance criteria**
- For LunaGlow Sunscreen template, at least **one** of A/B/C returns `guardrails_report.status = "pass"` with required terms present.

### A2) UI: show compliance badge + issues + auto-fix
On each creative card:
- Show a small badge:
  - `✅ Compliant` when pass
  - `⚠️ Needs fix` when needs_fix
- Add a “View issues” expander (list of issues + suggested fixes).
- Add a **one-click button**: `Auto-fix copy`
  - Calls a backend endpoint that takes the full variant + plan.guardrails and returns an updated variant where copy is edited to satisfy guardrails.
  - Should update “Changed fields” list (hook/primary_text/headline/disclaimer) similarly to how spec_patch changes are shown.

**Suggested endpoint (keep simple)**
- `POST /apply-guardrails`
  - Input: `{ variant: CreativeVariant, guardrails: Guardrails }`
  - Output: `CreativeVariant` + `{ changed_fields: [...] }`
- If you want to avoid new endpoint: fold it into `/regenerate-image` as a “copy_patch” mode, but new endpoint is clearer.

### A3) Export + evidence pack includes guardrails
- Export JSON should include:
  - plan.guardrails
  - each variant.guardrails_report
  - if auto-fix used: the changed_fields list
- Update `backend/scripts/generate_demo_outputs.py` to:
  - Run a guardrails-heavy template (LunaGlow)
  - Ensure at least 1 variant is compliant (either by default generation or by auto-fix)
  - Record the pass in `summary.md`

---

## Task B — Eliminate raw “Failed to fetch” everywhere

Even if the UI already *usually* shows friendly errors, make sure no path leaks raw fetch errors.

### B1) Centralize error mapping
- In `frontend/src/api.js`, wrap fetch so that any network error produces a friendly message like:
  - “Can’t reach backend at http://localhost:8000. Is it running?”
- Ensure this wrapper is used by:
  - /experiment-plan
  - /creative-variants
  - /score-creatives
  - /results
  - /regenerate-image
  - /explore-variants (both grids)
  - /health ping

### B2) Add one “debug detail” affordance (optional)
- A small “Details” accordion that shows the HTTP status + endpoint, but only if expanded (keep judges happy, keep devs informed).

**Acceptance criteria**
- You can kill the backend and the UI never shows literal text “Failed to fetch”.
- It shows a friendly message + Retry.

---

## Task C — Score scale clarity (avoid judge confusion)

Right now the app can show scores as X.X/10 in some places; we must ensure the entire UI is consistent.

### C1) Pick one scale and label it
Option 1 (recommended): **0–10** everywhere
- Cards show: `🌟 6.3/10`
- Winner card shows overall + dimension breakdown (also /10)

Option 2: **0–100** everywhere
- Convert by multiplying by 10; display `%` or `/100`.

**Acceptance criteria**
- No mix of /10 and /100 in different screens.
- Winner card + exploration grids match the same scale.

---

## Task D — Quick QA + artifact regeneration

1) Run app locally (mock mode OK) and execute DEMO_SCRIPT.md end-to-end.
2) Confirm:
   - Online badge works
   - Grid popouts work
   - Regeneration before/after works
   - Guardrails: at least one `✅ Compliant` (or show auto-fix to make it compliant)
   - Export includes guardrails + reports
3) Re-run evidence generator and zip the new run folder.

Deliverables
- PR / commit with changes above
- Updated evidence pack run folder + summary
