# Antigravity – Next Tasks (Post-Frontend Evidence Merge)

You crushed the frontend evidence work. Next we need to lock down **judge survivability** + create a small **evidence pack** that backs us up if a judge can’t run locally.

## Task A — Judge Quickstart in README (highest priority)
**Goal:** A judge can run the app in 2–3 commands with minimal friction.

### A1) Add/confirm a “Judge Quickstart” section near the top
Include:
- Prereqs: Node (18/20), Python (3.10+), Git
- Backend run steps (venv + pip + uvicorn)
- Frontend run steps (npm install + npm run dev)
- Where to set the Bria key (env var + .env guidance)
- What “success” looks like (LIVE badge, non-placeholder URL)

**Suggested wording**
- “Set `FIBO_API_KEY` (Bria Production key) as an env var or in `backend/.env`.”
- “Restart uvicorn after setting the key.”
- “If you see `Mock ⚠️`, the key isn’t loaded or Bria call failed.”

### A2) Add a 6-line Troubleshooting block
- Seeing **Mock ⚠️** → key not loaded, restart backend, verify env var
- Getting 401/403 → wrong key / permissions
- Still placeholder URLs → Bria unreachable or request failing; check backend logs
- Port conflicts → use `--port 8001` / set Vite port

### A3) Ensure secrets are safe
- Confirm `.env` and `backend/.env` are in `.gitignore`
- Never print keys in logs
- Never commit sample keys

---

## Task B — Backend sanity & contract lock (no demo surprises)
**Goal:** Ensure the frontend and backend agree exactly on the regenerate contract.

### B1) Confirm `/regenerate-image` expects:
```json
{
  "creative_id": "...",
  "spec_patch": {
    "camera_angle": "...",
    "shot_type": "...",
    "lighting_style": "...",
    "color_palette": "...",
    "background_type": "...",
    "prompt": "optional override"
  }
}
B2) Error handling clarity
If Bria call fails, return a clean error message that frontend can display.

Ensure we set image_status clearly: live vs mocked vs error (or similar).

B3) Log one line per regenerate
Example:

regenerate-image creative_id=... status=live
(Do NOT log any secrets.)

Task C — Add demo_outputs/ evidence pack (backup proof)
Goal: If a judge can’t run locally, they can still see we used FIBO + JSON control.

Create folder: demo_outputs/

C1) Add 3 spec patch JSON files (safe to commit)
product_shot.json

lifestyle.json

punchy_ad.json

Each should match the presets (camera angle, shot type, lighting, palette, background, optional prompt).

C2) Add 2–6 screenshots (or omit if we prefer no images in repo)
If included, screenshots should show:

LIVE badge ✅

Before/After panel after regeneration

Preset buttons

C3) Add demo_outputs/README.md
Keep it short:

“Changed X → got Y” bullets

Mention that this is a backup proof pack