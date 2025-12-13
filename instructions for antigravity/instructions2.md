# Antigravity – Final Submission Readiness Tasks (No Browser Needed)

You already verified the UI manually with Bria LIVE. Now we just need to “package it for judges” so the repo + submission are bulletproof even if they don’t run it locally.

## Task 1 — README: Judge Quickstart (Top priority)
**Goal:** A judge can run the app in 2–3 commands and immediately confirm Bria FIBO usage.

### 1A) Add a “Judge Quickstart” section near the top of README
Include:
- Prereqs: Node 18/20, Python 3.10+, Git
- Backend run commands
- Frontend run commands
- Where to set `FIBO_API_KEY` (Bria Production key)
- “What success looks like”: **LIVE badge** + **non-placeholder image URLs**
- Mention fallback behavior: **Mock badge** if key missing

### 1B) Add a Troubleshooting block (keep it short)
- Seeing **Mock ⚠️** → env var not loaded; restart backend; verify `FIBO_API_KEY` is set
- 401/403 from Bria → wrong key / permissions
- Port busy → change ports
- If regenerate errors → check backend logs (but no secrets printed)

### 1C) Confirm secrets are ignored
Ensure `.gitignore` includes:
```gitignore
.env
backend/.env
