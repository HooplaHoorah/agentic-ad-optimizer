# Agentic Ad Optimizer - Evidence Pack

This directory contains curated evidence of the Agentic Ad Optimizer's capabilities, specifically focusing on **FIBO (Fill-In-The-Background-Object)** control and **Compliance Guardrails**.

## Structure

- `spec_patches/`: JSON presets used to control image generation style (Lighting, Camera, Background).
- `guardrails_examples/`: Examples of guardrails configurations (e.g. LunaGlow Sunscreen).
- `example_payloads/`: Small JSON snippets showing API contracts (Auto-fix, Fast Explore).
- `run_*/`: Locally generated full run artifacts (Git-ignored to keep repo light).

## Key Features Demonstrated

1.  **Agentic Loop**: Snapshot -> Plan -> Creatives -> Scoring -> Results.
2.  **FIBO Integration**: All images are generated via Bria FIBO with controllable specs (`lighting_style`, `shot_type`, etc.).
3.  **Visual Exploration Grid**: A systematic agentic exploration of the design space (e.g. 8 variants varying lighting/palette).
4.  **Guardrails & Auto-Fix**: Real-time enforcement of brand safety (e.g. removing "cure" claims, adding "reef-safe").

## How to Generate Full Evidence

Run the generator script locally:

```bash
python backend/scripts/generate_demo_outputs.py
```

This will create a `demo_outputs/run_<timestamp>/` directory containing:
- Full JSON payloads for every step.
- All generated images.
- A detailed `summary.md`.

## Latest Verified Run

Latest local run: `run_20251213_123209` (Verified manually)
- Validated "LunaGlow Sunscreen" scenario.
- Confirmed Auto-fix removes "guaranteed/cure".
- Confirmed Fast Explore (4 variants) and Full Explore (8 variants) capability.
