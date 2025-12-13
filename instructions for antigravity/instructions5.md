# Antigravity Instructions 5 — “Failed to fetch” Fix + P0+ Micro-Upgrades (Top Prize Push)

Drop this file into the repo for reference. Goal: **remove any judge-scary UI glitches** and add the **smallest high-leverage features** that maximize scoring on Usage (FIBO), Impact, Innovation.

---

## 0) Deliverable format
Work in small PRs (or one PR) with:
- Before/after screenshots in the PR description
- No secrets in logs/screenshots
- A short “How to demo in 90 seconds” note at the end

---

## 1) Kill the “Failed to fetch” banner (P0+ polish — high judge impact)

### Why it matters
Even if everything works, a visible **“Failed to fetch”** reads as instability to judges. We want either:
- no banner at all, or
- a **friendly, actionable** message.

### Fix A — Clear error on step transitions (fastest win)
Implement one of:
- `useEffect(() => setError(""), [step]);`
- Or `setError("")` inside *Next*, *Back*, and *Skip to results* handlers.

**Acceptance:** If a request fails on Step 1, then user moves to Step 2/3, the old error **does not persist**.

### Fix B — Friendly error mapping (no raw browser text)
In the API wrapper, detect network errors and replace with:

> “Backend not reachable at http://localhost:8000. Start backend and retry.”

Also add a hint if `FIBO_API_KEY` is missing (if that’s detectable), but don’t block the demo.

**Acceptance:** “Failed to fetch” never appears in UI.

### Fix C — Add a one-click Retry
When banner is shown, include a **Retry** button that replays the last action:
- last endpoint + last payload (store in state)
- or a simple “Retry last call” handler per step

**Acceptance:** A network blip can be recovered without refreshing.

### What to report back
- Screenshot: banner state + the new friendly text + Retry button
- 10-second screen recording: trigger an error (stop backend), show Retry working after restart

---

## 2) Make FIBO usage “undeniable” on-screen (P0+ scoring booster)

### Feature A — “Spec Inspector” per creative (minimal UI)
Add a small expandable panel on each creative card:
- Show **fibo_spec JSON** (collapsed by default)
- Button: **Copy JSON**
- Show `image_status` (fibo / mocked / error) right next to the image

**Acceptance:** Judge can see exact parameters driving the image, without reading code.

### Feature B — Highlight what changed on regeneration
When user regenerates, show:
- “Changed fields:” list (keys from spec_patch)
- Optional: show values before → after for those keys

**Acceptance:** A judge can visually connect: “We changed lighting_style and shot_type and got a different image.”

### What to report back
- Screenshot: one creative card expanded showing fibo_spec + copy button
- Screenshot: regen history entry showing changed fields + before/after thumbnails

---

## 3) One “wow” preset: Lock composition, change only lighting (Innovation w/ tiny effort)

Add a preset button like:
- **Lock framing, try warmer lighting**
- The preset should only patch 1–2 fields (e.g., `lighting_style`, `color_palette`) and leave others intact.

**Acceptance:** Before/after looks like a controlled experiment (not random).

**Report:** screenshot of the patch JSON + resulting before/after images.

---

## 4) Evidence Pack for judges (repo-proof even if they don’t run locally)
Create `demo_outputs/`:
- `product_shot.json`, `lifestyle.json`, `punchy_ad.json`, `lock_lighting.json`
- `demo_outputs/README.md` with bullet explanations: “Changed X → got Y”
- 3–6 screenshots (LIVE badge, presets, before/after, winner card, export)

**Acceptance:** A judge can verify FIBO controllability by reading repo only.

**Report:** tree listing + screenshots added.

---

## 5) Final walkthrough checklist (what I want you to send me after the PR)
Please send:
1) The PR link(s)
2) A 60–90 second screen recording of the “golden path” demo
3) 5 screenshots:
   - Template selected + business snapshot filled
   - Creatives generated
   - Spec Inspector expanded
   - Regen before/after with changed fields
   - Winner card + export done
4) If anything still ever says “Failed to fetch,” include:
   - Browser console log
   - Network tab for the failing request
   - Backend log line around the failure

---

## 6) Demo script (90 seconds)
1) Choose template → Generate plan → Generate creatives
2) Expand Spec Inspector → point at fibo_spec
3) Click Lock Lighting preset → Regenerate → point at changed fields + before/after
4) Score → Get recommendation → show winner rationale
5) Export → “handoff-ready artifacts”
