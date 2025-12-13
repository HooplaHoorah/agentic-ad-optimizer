# instructions6.md — Phase 3.1 “Top-prize contender” upgrades (Grid Search + Evidence Pack + Error polish)

Context: P0 + Phase 2 polish are done (3-step demo, FIBO LIVE, Spec Inspector JSON, changed-fields, regenerate flow, export button, start-over, port=8000).

This phase is about *judge impact*: make it obvious we’re **exploring FIBO JSON space agentically**, and leave behind a **reproducible evidence pack** (JSON + images) for DevPost.

---

## A) Lock Lighting preset: treat as **real** (no webhook) + doc cleanup

1) **Verify behavior**
- Click **Lock Lighting** on a variant and regenerate.
- Confirm request payload includes a `spec_patch` that sets only:
  - `lighting_style`
  - `color_palette`
  - (optionally) a prompt hint like “same framing, warmer lighting…”
- Confirm response returns the updated variant with:
  - merged `fibo_spec`
  - `image_status` = `fibo` (or `mocked` if no key)
  - changed-fields list reflects only those fields

2) **Remove/replace any “webhook required” note**
- If any doc or UI tooltip says the preset needs a webhook, update it to:
  - “This preset just sends a spec_patch to /regenerate-image (no webhook).”
- If there *is* a stubbed webhook path in code, keep it optional (future) but don’t block the preset.

**Acceptance:** preset works end-to-end in LIVE mode and docs do not mention webhook dependency.

---

## B) Add a “Visual Exploration Grid” (8 variants) — biggest judge wow for minimal code

Goal: with one click, show the agent exploring controlled FIBO dimensions and producing a grid of images **with JSON patches visible**.

### UX (frontend)
Add a button on each creative card:
- Label: **Explore 8 visual variants**
- On click:
  - choose that variant as the “base”
  - call backend endpoint (below)
  - render returned variants in a small grid under the card (2x4 or 4x2)
  - each tile shows:
    - image
    - tiny badge of what changed (e.g., “warm+gold”, “cool+pastel”, “studio”, “lifestyle”, etc.)
    - a “View JSON” toggle (reuse Spec Inspector component)

Suggested axes (2×2×2 = 8):
- `lighting_style`: warm vs cool
- `color_palette`: warm_golden vs pastel
- `background_type`: studio vs natural

(If your schema differs, adapt to whatever keys you already support.)

### API (backend)
Add a new endpoint, e.g.:
- `POST /explore-variants`

Request:
```json
{
  "base_variant": { ...full CreativeVariant... },
  "axes": {
    "lighting_style": ["warm", "cool"],
    "color_palette": ["warm_golden", "pastel"],
    "background_type": ["studio", "natural"]
  }
}
```

Response:
```json
{
  "base_variant_id": "...",
  "generated": [ ...list[CreativeVariant] ... ],
  "meta": {
    "count": 8,
    "runtime_ms": 12345
  }
}
```

Implementation approach:
- Generate the cartesian product of the axis choices (8 combos).
- For each combo, call the existing regeneration logic **internally** (same function used by `/regenerate-image`), with a `spec_patch` set to just those axis values.
- Return the 8 updated variants.

Notes:
- Keep it safe if no API key: return `image_status=mocked` and a placeholder image URL, but still return the merged `fibo_spec` so the UI shows JSON control.
- Add a very small log line per generated variant (no secrets).

**Acceptance:** one click produces 8 visibly different images + each has Spec JSON accessible + changed-fields make sense.

---

## C) Evidence Pack: auto-write `demo_outputs/` artifacts for DevPost

Judges love receipts. Make it easy to generate and commit a “proof folder”.

### Option 1 (recommended): CLI script
Add:
- `backend/scripts/generate_demo_outputs.py`

What it does:
- Runs a deterministic demo scenario:
  1) generate plan
  2) generate creatives
  3) score creatives
  4) regenerate one variant with a preset patch (e.g., Lock Lighting)
  5) run exploration grid (8 variants)
- Writes:
  - `demo_outputs/run_<timestamp>/summary.md`
  - `demo_outputs/run_<timestamp>/payloads/*.json` (requests + responses)
  - `demo_outputs/run_<timestamp>/images/*.png` (download the returned image URLs if possible)
  - `demo_outputs/run_<timestamp>/README.md` with “how to reproduce”

### Option 2: extend existing Export button
If export already produces a zip, enhance it to include:
- all fibo specs (before/after)
- exploration grid outputs
- summary markdown

**Acceptance:** `demo_outputs/` can be generated in one command and contains JSON + images + a short summary.

---

## D) “Failed to fetch” polish (make errors demo-proof)

Even if it’s “just local,” the UI should explain exactly what to do.

Frontend:
- When a fetch fails (network error), show:
  - “Backend unreachable. Start it with: uvicorn backend.app.main:app --reload --port 8000”
- When backend returns non-2xx:
  - show status code + friendly message
- Ensure error banners clear after a successful step (keep current behavior).

Backend:
- Ensure CORS allows the Vite origin (5173).
- Ensure /health exists (optional) so UI can detect backend before first request.

**Acceptance:** if backend is down, the UI tells the user the exact fix; no cryptic “Failed to fetch”.

---

## Quick demo script delta (add 10–15 seconds)
In `DEMO_SCRIPT.md`, add:
- “Now I’ll click Explore 8 visual variants — notice we’re changing only lighting/palette/background via FIBO JSON, and you can inspect the exact spec.”

---

## Deliverables checklist
- [ ] Lock Lighting docs corrected (no webhook dependency)
- [ ] `/explore-variants` backend endpoint
- [ ] “Explore 8 visual variants” button + grid UI
- [ ] `demo_outputs/` generator (CLI or export enhancement)
- [ ] Error messaging replaces “Failed to fetch” with actionable guidance
