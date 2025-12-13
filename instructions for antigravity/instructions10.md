# instructions10.md — Phase 3.4: Demo-Speed Explore + Realistic Guardrails Evidence (Final “Judge Confidence” Polish)

Context
- Phase 3.3 is complete (guardrails enforced + auto-fix, friendly errors, scoring scale, evidence pack generation).
- Remaining risk: **demo timing + credibility**.
  - In LIVE mode, 8-variant exploration can take ~2+ minutes (too long for a judge demo).
  - Current auto-fix evidence uses “barista-quality / warmup” terms that don’t match the SaaS/DTC templates (can look contrived).

Goal
1) Make Explore feel **instant/fast** in a live demo.
2) Make guardrails examples **plausible for the chosen template** (e.g., sunscreen / cosmetics / finance / health).

---

## A) Add “Fast Explore” (4 variants) and keep “Full Explore” (8 variants)

### A1) Frontend UI
On each creative card, replace/augment the current Explore button with:
- **Explore (Fast 4)** — default button
- **Explore (Full 8)** — secondary/overflow action (or behind “Advanced”)

Behavior:
- If `/health.mode == "live"`:
  - Default to **Fast 4**
- If mocked:
  - Allow Full 8 by default (fast anyway)

Copy (judge-friendly):
- Fast 4: “~20–40s LIVE, instant in MOCKED”
- Full 8: “May take ~2 minutes LIVE”

### A2) Backend endpoint: support a bounded 4-variant mode
Update `POST /explore-variants` to accept either:
- `preset: "fast4" | "full8"` **or**
- `max_variants: 4 | 8`

Implementation (simple + deterministic):
- For **fast4**, explore 2 axes (2×2 = 4), e.g.:
  - `lighting_style`: warm vs cool
  - `color_palette`: warm_golden vs pastel
- For **full8**, keep 3 axes (2×2×2 = 8), current behavior.

**Acceptance**
- In LIVE mode, Fast4 returns in a time that is demo-appropriate.
- Full8 remains available.

### A3) UX: non-scary progress
Without adding streaming complexity, update the UI to show:
- “Generating 4 variants…”
- When done: “Done (4/4)”

(If you already have a spinner, just improve the label.)

**Report back**
- Screenshot: buttons/labels
- Runtime in LIVE for fast4 and full8 (rough)

---

## B) Make guardrails + auto-fix evidence *believable*

### B1) Update the evidence generator script to use **template-consistent** guardrails
In `backend/scripts/generate_demo_outputs.py`, ensure the “guardrails run” uses a real template and realistic constraints.

Suggested guardrails by template:

**DTC ecom (LunaGlow Sunscreen)**
- required_terms: `reef-safe`, `broad-spectrum`, `SPF 50`
- avoid_words: `cure`, `guaranteed`
- disclaimer: `Reapply every 2 hours and after swimming/sweating.`
- regulated_category: `health` (or `none` if you prefer)

**SaaS (FlowPilot AI Scheduler)**
- required_terms: `early access`, `free trial`
- avoid_words: `guaranteed`, `instant`
- disclaimer: `Features may change during beta.`
- regulated_category: `none`

### B2) Make the auto-fix demo input match the template
If you intentionally inject “bad copy” for auto-fix, make it plausible:
- For sunscreen: “guaranteed to cure sun damage instantly” → should be censored/removed
- For SaaS: “instant guaranteed results” → censored/removed

Then auto-fix should:
- remove/censor banned words
- append missing required terms
- append disclaimer

### B3) Ensure the UI tells the story
On the card, for Needs fix:
- show the failing rule(s) (e.g., “Missing: reef-safe”, “Contains banned word: guaranteed”)
After auto-fix:
- badge flips to ✅ Compliant
- show “Fixed fields: hook, primary_text, headline” (see Task C)

**Acceptance**
- Evidence pack shows a believable scenario and reads like real marketing compliance.
- No weird domain mismatch terms like “barista-quality” in a SaaS run.

**Report back**
- New `demo_outputs/run_*/summary.md` excerpt showing:
  - chosen template
  - guardrails
  - failing copy → fixed copy (short)
- The `05c_auto_fix_*.json` payload pair for that run

---

## C) (Small) Add `changed_fields` to `/apply-guardrails` response (nice-to-have polish)
Right now the UI may infer changes, but for evidence/exports it’s cleaner to include it.

Update response schema to:
```json
{
  "variant": { ...CreativeVariant... },
  "changed_fields": ["hook", "primary_text"]
}
```

Compute by comparing incoming vs outgoing text fields:
- hook / primary_text / headline / cta / disclaimer

**Acceptance**
- UI uses this list to display “Fixed fields: …”
- Evidence pack stores it in `05c_auto_fix_response.json`

---

## Definition of done
- [ ] Fast4 explore exists + is default in LIVE mode
- [ ] Evidence pack guardrails are template-consistent and believable
- [ ] Auto-fix demo uses plausible banned words for the template
- [ ] (Optional) `/apply-guardrails` returns `changed_fields`
