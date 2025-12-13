# Google Antigravity – P0+ Sprint Instructions (Agentic Ad Optimizer / FIBO Hackathon)

Owner: Hoopla Hoorah  
Goal: Make the project **judge-proof** (it must still “sell” even if a judge can’t run it) and **top-prize-contender** on the 3 scoring axes: Usage of FIBO, Impact, Innovation.

## A. What’s already green (do NOT redo)
- `/regenerate-image` contract is stable and wired end-to-end.
- Frontend regen shows before/after + timestamps.
- Presets exist (Product Shot / Lifestyle / Punchy Ad).
- Backend+frontend ports aligned (8000 + 5173/5174).

## B. P0+ items to implement / verify (highest leverage)

### 1) Campaign Templates (Impact)
**Goal:** a judge can pick a realistic scenario in 1 click and get a coherent plan + creatives (no blank-page vibe).

Implement:
- Add a **Campaign Template dropdown** in the “Business Snapshot” step with 3 presets:
  1) DTC ecom (e.g., “LunaGlow Sunscreen”)
  2) SaaS (e.g., “FlowPilot AI scheduler”)
  3) Local service (e.g., “Austin Mobile Detailing”)
- Each template should prefill: brand, audience, offer, channel, tone, constraints.

Acceptance:
- Template load is **idempotent** (can switch templates without breaking state).
- Each template creates an experiment plan and generates creatives successfully.

Report back with:
- Screenshot of the dropdown + one filled template.

### 2) Exportable Artifacts (Impact + Innovation)
**Goal:** “handoff-ready” deliverables for marketers + proof for judges.

Implement:
- Add an **Export** button on the Results page that downloads a single bundle (zip preferred, or a folder structure + instructions):
  - `experiment_plan.json`
  - `creative_variants.json` (full objects, incl. fibo_spec + image_status + image_url)
  - `scores.json` (per-variant score breakdown)
  - `recommendation.json` (winner + next-test suggestion)
  - `spec_patches_used/` (the JSON patches applied)

Acceptance:
- Export works without secrets.
- Bundle contains enough info to recreate or audit the demo.

Report back with:
- The generated zip (or listing) and a 10-line note: “what’s inside”.

### 3) Evidence Pack (Backup proof if app won’t run)
**Goal:** judges can still see FIBO controllability in-repo.

Implement:
- Create `demo_outputs/` containing:
  - `product_shot.json`, `lifestyle.json`, `punchy_ad.json` (the actual spec_patch JSON)
  - `demo_outputs/README.md` that explains: “Changed X → got Y” in bullet form
  - 2–6 screenshots showing: LIVE badge, preset buttons, before/after panel

Acceptance:
- No generated images committed unless tiny/necessary; screenshots are fine.
- README is clear without needing to run the app.

Report back with:
- Tree listing of `demo_outputs/` + screenshots.

### 4) Judge Quickstart Hardening (Usage)
**Goal:** 2–3 commands to run; obvious “success” state.

Implement:
- Confirm README includes:
  - exact backend + frontend run steps
  - where to set `FIBO_API_KEY` (Production)
  - what “success” looks like (LIVE badge + non-placeholder URLs)
  - troubleshooting: Mock badge / key missing / backend not reachable

Acceptance:
- Fresh clone → following README works with no guesswork.

Report back with:
- Exact README section diffs.

### 5) Make the “agentic” loop judge-visible (Innovation)
**Goal:** the app narrates *why* a creative won and what it will try next.

Implement (minimal UI copy, no big refactor):
- In Results, show:
  - winner (with image + key fibo_spec fields)
  - score breakdown per dimension
  - a “Next test suggestion” that references FIBO parameters (e.g., “Try warmer lighting + tighter crop for clarity”)

Acceptance:
- A judge can point at the screen and say “this is agentic optimization”.

Report back with:
- Screenshot of Results explaining winner + next step.

## C. Final deliverables to push
- PR(s) to `main` or one PR with all above
- Ensure `.env` / keys are ignored
- No secrets in screenshots

## D. Smoke test checklist (run before recording)
1) Start backend + frontend fresh
2) Load a Campaign Template → generate plan → generate creatives
3) Use each preset → regenerate → confirm before/after updates
4) Run scoring + recommendation once
5) Export bundle downloads successfully
