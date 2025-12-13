# instructions10a.md — Demo Outputs “Evidence Pack” Policy + Repo Hygiene (Antigravity)

Goal: keep **judge-proof receipts** in the repo *without bloating it*, while still allowing repeatable generation of full run artifacts locally.

This is *only* about `demo_outputs/` and related `.gitignore` / export behaviors.

---

## 1) What we want in the repo vs. what we keep local

### ✅ COMMIT to the repo (small, curated, judge-friendly)
Create/keep a **curated evidence pack** in `demo_outputs/`:

**Required**
- `demo_outputs/README.md`
  - Explains what FIBO JSON control is
  - Explains presets + regeneration + explore grid
  - Explains guardrails + auto-fix
  - Explains how to run the generator script
  - Links to where the “full” artifacts are produced locally (`run_*/`)

**Recommended (small JSON only)**
- `demo_outputs/spec_patches/`
  - `product_shot.json`
  - `lifestyle.json`
  - `punchy_ad.json`
  - `lock_lighting.json`
- `demo_outputs/guardrails_examples/`
  - `lunaglow_guardrails.json` (reef-safe, broad-spectrum, SPF 50 + “reapply every 2 hours …”)
  - `saas_guardrails.json` (early access, free trial + beta disclaimer)
- `demo_outputs/example_payloads/` (keep these *tiny*)
  - `apply_guardrails_example_request.json`
  - `apply_guardrails_example_response.json`
  - `explore_fast4_example_response.json`

**Optional**
- A *small* set of optimized screenshots (max 5, compressed):
  - `demo_outputs/screenshots/01_template.png`
  - `demo_outputs/screenshots/02_live_badge.png`
  - `demo_outputs/screenshots/03_spec_inspector.png`
  - `demo_outputs/screenshots/04_before_after.png`
  - `demo_outputs/screenshots/05_explore_grid.png`

> If screenshots are large (or we want zero images in git), keep them OUT of the repo and just describe them in README.

### ❌ DO NOT COMMIT (generated per-run artifacts)
These should be generated locally and ignored:
- `demo_outputs/run_*/` (entire directory trees)
- `demo_outputs/**/images/` (downloaded/generated images)
- Any large zip exports or video recordings

---

## 2) `.gitignore` rules (recommended exact patterns)

Update `.gitignore` to **NOT** ignore the entire folder.

✅ Keep curated files:
- `demo_outputs/README.md`
- `demo_outputs/spec_patches/**`
- `demo_outputs/guardrails_examples/**`
- `demo_outputs/example_payloads/**`
- (optional) `demo_outputs/screenshots/**` if kept small

Ignore generated runs + heavy files:

```gitignore
# Demo outputs: keep curated evidence, ignore generated runs
demo_outputs/run_*/
demo_outputs/**/images/
demo_outputs/**/*.zip
demo_outputs/**/*.mp4
demo_outputs/**/*.mov
demo_outputs/**/*.webm

# If screenshots are large, ignore them too (optional)
# demo_outputs/screenshots/
```

**Acceptance**
- `git status` shows curated evidence pack files tracked
- No run folders or images show up as untracked changes after running the generator

---

## 3) Evidence generator behavior (backend/scripts/generate_demo_outputs.py)

### 3.1 Output layout (standardize)
Ensure the script writes to:
- `demo_outputs/run_<timestamp>/`
  - `summary.md`
  - `payloads/*.json`
  - `images/*` (if downloading images)
  - `meta.json` (optional: runtime, mode live/mocked, axis config)

### 3.2 Template-consistent guardrails (credibility)
When generating “auto-fix” evidence, use guardrails that match the chosen template:

**LunaGlow Sunscreen**
- required_terms: `reef-safe`, `broad-spectrum`, `SPF 50`
- avoid_words: `guaranteed`, `cure`
- disclaimer: `Reapply every 2 hours and after swimming/sweating.`

**SaaS**
- required_terms: `early access`, `free trial`
- avoid_words: `guaranteed`, `instant`
- disclaimer: `Features may change during beta.`

**Acceptance**
- `summary.md` clearly states the template + guardrails
- Auto-fix examples don’t use weird domain-mismatched terms (e.g., “barista-quality” in SaaS)

---

## 4) Curated evidence refresh workflow (what to do before a major push)

### Step A — run generator locally
- Run `python backend/scripts/generate_demo_outputs.py`
- Confirm a new `demo_outputs/run_*/` folder is created

### Step B — copy tiny examples into curated folders
From that run, extract **small** representative JSON (trim large arrays if needed) into:
- `demo_outputs/example_payloads/`
- `demo_outputs/guardrails_examples/`

### Step C — update `demo_outputs/README.md`
Add:
- “Latest verified run: run_YYYYMMDD_HHMMSS (local)”
- Bullet recap of what it proves (regen, explore, guardrails, auto-fix)
- A note that full run artifacts are intentionally ignored to keep repo small

### Step D — verify git cleanliness
- `git status` should only show curated files changed
- No `run_*/` directories staged

---

## 5) Definition of done (for this ticket)
- [ ] `.gitignore` no longer ignores all of `demo_outputs/`
- [ ] Curated evidence pack exists in repo (README + small JSON examples)
- [ ] Generated runs (`demo_outputs/run_*`) remain ignored
- [ ] Generator produces a clean run folder with `summary.md` + payloads
- [ ] Guardrails examples are template-consistent and believable
