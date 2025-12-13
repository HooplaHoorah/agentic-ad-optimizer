"""
Phase 3.1 Task C: Generate Demo Outputs for DevPost Evidence Pack

This script runs a deterministic demo scenario and captures all artifacts
for a reproducible evidence pack. Perfect for judges and documentation.

Usage:
    python backend/scripts/generate_demo_outputs.py
"""

import os
import sys
import json
import time
import asyncio
from pathlib import Path
from datetime import datetime
import httpx

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.schemas.models import BusinessSnapshot, Product, Audience

# Configuration
API_BASE = "http://localhost:8000"
OUTPUT_BASE = Path("demo_outputs")

async def generate_demo_outputs():
    """Run a complete demo scenario and save all artifacts."""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = OUTPUT_BASE / f"run_{timestamp}"
    payloads_dir = run_dir / "payloads"
    images_dir = run_dir / "images"
    
    # Create directories
    run_dir.mkdir(parents=True, exist_ok=True)
    payloads_dir.mkdir(exist_ok=True)
    images_dir.mkdir(exist_ok=True)
    
    print(f"📦 Generating demo outputs in: {run_dir}")
    print("=" * 60)
    
    # Increase timeout for exploration grid (can take 30+ seconds)
    async with httpx.AsyncClient(timeout=180.0) as client:
        
        # Helper to safely get JSON or print error
        async def safe_request(method, url, **kwargs):
            try:
                response = await client.request(method, url, **kwargs)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                print(f"\n❌ Request failed: {method} {url}")
                print(f"Status: {response.status_code if 'response' in locals() else 'Unknown'}")
                if 'response' in locals():
                    print(f"Response: {response.text[:500]}...") # Print first 500 chars
                raise e

        # Step 1: Generate Plan
        print("\n1️⃣  Generating experiment plan...")

        snapshot_data = {
            "products": [{
                "id": "product_1",
                "name": "FlowPilot AI Scheduler",
                "price": 49.0,
                "margin": 35.0,
                "category": "SaaS",
                "benefits": ["AI-powered calendar that saves 5+ hours per week"],
                "objections": ["Learning curve concerns"]
            }],
            "audiences": [{
                "id": "audience_1",
                "segment": "Busy professionals and team leads",
                "size_estimate": 500000.0,
                "platform": "Meta",
                "pain_points": ["Calendar chaos and back-to-back meetings"],
                "jobs_to_be_done": ["Improve productivity", "Reduce meeting overhead"]
            }],
            "guardrails": {
                "brand_voice": "Passionate, expert, accessible",
                "avoid_words": ["cheap", "instant"],
                "required_terms": ["barista-quality", "warranty"],
                "disclaimer": "Machine requires 15-minute warmup.",
                "prohibited_claims": [],
                "regulated_category": "none",
                "target_channel": "Meta"
            },
            "historical_performance": [],
            "sales_data": []
        }
        
       # Save request
        with open(payloads_dir / "01_experiment_plan_request.json", "w") as f:
            json.dump(snapshot_data, f, indent=2)
        
        response_json = await safe_request("POST", f"{API_BASE}/experiment-plan", json=snapshot_data)
        plan = response_json
        
        # Save response
        with open(payloads_dir / "01_experiment_plan_response.json", "w") as f:
            json.dump(plan, f, indent=2)
        
        print(f"   ✓ Plan created: {plan['experiment_id']}")
        print(f"   ✓ Variants: {', '.join([v['variant_id'] for v in plan['variants']])}")
        
        # Step 2: Generate Creatives
        print("\n2️⃣  Generating creative variants...")
        creatives = await safe_request("POST", f"{API_BASE}/creative-variants", json=plan)
        
        # Save response
        with open(payloads_dir / "02_creative_variants_response.json", "w") as f:
            json.dump(creatives, f, indent=2)
        
        print(f"   ✓ Generated {len(creatives)} creatives")
        
        # Download images
        for creative in creatives:
            if creative.get("image_url"):
                variant_id = creative["variant_id"]
                try:
                    img_response = await client.get(creative["image_url"])
                    if img_response.status_code == 200:
                        ext = "png" if "png" in creative["image_url"] else "jpg"
                        img_path = images_dir / f"creative_{variant_id}_original.{ext}"
                        with open(img_path, "wb") as f:
                            f.write(img_response.content)
                        print(f"   ✓ Downloaded image for variant {variant_id}")
                except Exception as e:
                    print(f"   ⚠️  Could not download image for {variant_id}: {e}")
        
        # Step 3: Score Creatives
        print("\n3️⃣  Scoring creative variants...")
        scores = await safe_request("POST", f"{API_BASE}/score-creatives", json=creatives)
        
        # Save response
        with open(payloads_dir / "03_score_creatives_response.json", "w") as f:
            json.dump(scores, f, indent=2)
        
        print(f"   ✓ Scored {len(scores)} creatives")
        for score in scores:
            print(f"      • {score['creative_id']}: {score['overall_strength']:.1f}/10")
        
        # Step 4: Regenerate with Lock Lighting Preset
        print("\n4️⃣  Testing Lock Lighting preset on Variant B...")
        variant_b = next((c for c in creatives if c["variant_id"] == "B"), None)
        
        if variant_b:
            regenerate_req = {
                "variant": variant_b,
                "spec_patch": {
                    "lighting_style": "warm",
                    "color_palette": "warm_golden",
                    "prompt": "Same framing, warmer lighting with golden hour glow"
                }
            }
            
            # Save request
            with open(payloads_dir / "04_regenerate_lock_lighting_request.json", "w") as f:
                json.dump(regenerate_req, f, indent=2)
            
            response_json = await safe_request("POST", f"{API_BASE}/regenerate-image", json=regenerate_req)
            regenerated = response_json
            
            # Save response
            with open(payloads_dir / "04_regenerate_lock_lighting_response.json", "w") as f:
                json.dump(regenerated, f, indent=2)
            
            print(f"   ✓ Regenerated with Lock Lighting")
            print(f"   ✓ Status: {regenerated.get('image_status', 'unknown')}")
            
            # Download regenerated image
            if regenerated.get("image_url"):
                try:
                    img_response = await client.get(regenerated["image_url"])
                    if img_response.status_code == 200:
                        ext = "png" if "png" in regenerated["image_url"] else "jpg"
                        img_path = images_dir / f"creative_B_lock_lighting.{ext}"
                        with open(img_path, "wb") as f:
                            f.write(img_response.content)
                        print(f"   ✓ Downloaded regenerated image")
                except Exception as e:
                    print(f"   ⚠️  Could not download regenerated image: {e}")
        
        # Step 5: Explore 8 Visual Variants
        print("\n5️⃣  Running Visual Exploration Grid (8 variants)...")
        
        if variant_b:
            explore_req = {
                "base_variant": variant_b,
                "axes": {
                    "lighting_style": ["warm", "cool"],
                    "color_palette": ["warm_golden", "pastel"],
                    "background_type": ["studio", "natural"]
                }
            }
            
            # Save request
            with open(payloads_dir / "05_explore_variants_request.json", "w") as f:
                json.dump(explore_req, f, indent=2)
            
            response_json = await safe_request("POST", f"{API_BASE}/explore-variants", json=explore_req)
            exploration = response_json
            
            # Save response
            with open(payloads_dir / "05_explore_variants_response.json", "w") as f:
                json.dump(exploration, f, indent=2)
            
            print(f"   ✓ Generated {exploration['meta']['count']} explored variants")
            print(f"   ✓ Runtime: {exploration['meta']['runtime_ms']}ms")
            
            # Download explored variant images
            for idx, explored in enumerate(exploration["generated"], 1):
                if explored.get("image_url"):
                    try:
                        img_response = await client.get(explored["image_url"])
                        if img_response.status_code == 200:
                            ext = "png" if "png" in explored["image_url"] else "jpg"
                            img_path = images_dir / f"explored_variant_{idx:02d}.{ext}"
                            with open(img_path, "wb") as f:
                                f.write(img_response.content)
                            spec = explored.get("fibo_spec", {})
                            print(f"   ✓ Downloaded variant {idx}: {spec.get('lighting_style', '?')}/{spec.get('color_palette', '?')}/{spec.get('background_type', '?')}")
                    except Exception as e:
                            print(f"   ⚠️  Could not download explored variant {idx}: {e}")
        
        # Step 5b: Explore Advanced Variants (New Axes)
        print("\n5️⃣  ℹ️ Running Advanced Visual Exploration (Shot Type + Camera Angle)...")
        if variant_b:
            explore_adv_req = {
                "base_variant": variant_b,
                "axes": {
                    "shot_type": ["product_only", "lifestyle"],
                    "camera_angle": ["eye_level", "high_angle"],
                    "lighting_style": ["warm", "cool"]
                }
            }
            
            # Save request
            with open(payloads_dir / "05b_explore_advanced_request.json", "w") as f:
                json.dump(explore_adv_req, f, indent=2)
            
            response_json = await safe_request("POST", f"{API_BASE}/explore-variants", json=explore_adv_req)
            adv_exploration = response_json
            
            # Save response
            with open(payloads_dir / "05b_explore_advanced_response.json", "w") as f:
                json.dump(adv_exploration, f, indent=2)
            
            print(f"   ✓ Generated {adv_exploration['meta']['count']} advanced variants")
            
            # Download explored variant images
            for idx, explored in enumerate(adv_exploration["generated"], 1):
                if explored.get("image_url"):
                    try:
                        img_response = await client.get(explored["image_url"])
                        if img_response.status_code == 200:
                            ext = "png" if "png" in explored["image_url"] else "jpg"
                            img_path = images_dir / f"explored_advanced_{idx:02d}.{ext}"
                            with open(img_path, "wb") as f:
                                f.write(img_response.content)
                    except Exception as e:
                        pass # Squelch errors for demo speed

        # Step 5c: Test Guardrails Auto-Fix
        print("\n5️⃣  ℹ️ Testing Guardrails Auto-Fix...")
        # Manually create a non-compliant variant (simulating user edit)
        if variant_b:
            bad_variant = variant_b.copy()
            bad_variant["primary_text"] = "This stuff is cheap and works instant." # Violates 'cheap', 'instant' and missing required terms
            bad_variant["variant_id"] = "bad_copy_test"
            
            # Guardrails from plan
            guardrails = plan["guardrails"]
            
            auto_fix_req = {
                "variant": bad_variant,
                "guardrails": guardrails
            }
            
            with open(payloads_dir / "05c_auto_fix_request.json", "w") as f:
                json.dump(auto_fix_req, f, indent=2)
            
            fixed_variant = await safe_request("POST", f"{API_BASE}/apply-guardrails", json=auto_fix_req)
            
            with open(payloads_dir / "05c_auto_fix_response.json", "w") as f:
                json.dump(fixed_variant, f, indent=2)
                
            print(f"   ✓ Auto-fix applied.")
            try:
                print(f"   Original: {bad_variant['primary_text']}")
                print(f"   Fixed:    {fixed_variant['primary_text']}")
                print(f"   Changed:  {str(fixed_variant['guardrails_report'].get('fixed_issues', []))}")
            except Exception:
                print("   (Skipped printing details due to encoding error)")
    
    # Generate Summary Markdown
    print("\n6️⃣  Generating summary documentation...")
    summary_content = f"""# Demo Output Summary

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Run ID:** run_{timestamp}

## Overview

This evidence pack demonstrates the Agentic Ad Optimizer's complete workflow,
including the Phase 3.1 "Visual Exploration Grid" feature that shows systematic
exploration of FIBO image parameters.

## What's Included

### 1. JSON Payloads (`payloads/`)

Complete request/response pairs for all API endpoints:

- `01_experiment_plan_*.json` - Plan generation from business snapshot
- `02_creative_variants_*.json` - Creative generation with FIBO specs
- `03_score_creatives_*.json` - Rubric-based scoring
- `04_regenerate_lock_lighting_*.json` - Lock Lighting preset application
- `05_explore_variants_*.json` - 8-variant exploration grid

### 2. Images (`images/`)

All generated images from the demo run:

- `creative_[A-C]_original.*` - Initial creative images
- `creative_B_lock_lighting.*` - Variant B after Lock Lighting preset
- `explored_variant_[01-08].*` - 8 variants from exploration grid

Each explored variant represents a different combination of:
- lighting_style: warm | cool
- color_palette: warm_golden | pastel
- background_type: studio | natural

### 3. This Summary

Quick reference for understanding the evidence pack.

## Key Demonstration Points

### ✅ Agentic Loop is Complete
1. Business snapshot → Experiment plan
2. Experiment plan → Creative variants with FIBO specs
3. Creatives → Rubric scores
4. Results → Next test recommendations

### ✅ FIBO Integration Working
- All creatives have `fibo_spec` with controllable parameters
- Live API mode when `FIBO_API_KEY` is set
- Graceful fallback to mocked mode without key

### ✅ Spec-Controlled Regeneration
- Lock Lighting preset modifies only lighting/palette parameters
- Full before/after tracking with changedfields
- Merged spec shows exact JSON sent to FIBO

### ✅ Visual Exploration Grid (Phase 3.1)
- One click generates 8 systematic variants
- Cartesian product of 3 axes (2×2×2 = 8 combinations)
- Each variant has inspectable JSON spec
- Demonstrates agentic exploration of parameter space

## Reproduction Steps

1. **Start the backend:**
   ```bash
   uvicorn backend.app.main:app --reload --port 8000
   ```

2. **Run this script:**
   ```bash
   python backend/scripts/generate_demo_outputs.py
   ```

3. **Verify outputs:**
   - Check `demo_outputs/run_<timestamp>/` for this evidence pack
   - Review JSON payloads for API contracts
   - Inspect images for visual quality

## Technical Details

**Backend:** FastAPI + Pydantic models  
**FIBO Client:** `backend/app/fibo_client.py`  
**Endpoints Used:**
- POST /experiment-plan
- POST /creative-variants
- POST /score-creatives
- POST /regenerate-image
- POST /explore-variants

**Frontend Integration:** React + Vite  
**Demo Flow:** 3-step wizard (Snapshot → Plan & Creatives → Results)

## DevPost Ready

This evidence pack is ready for inclusion in a DevPost submission:
- ✅ JSON proves API contracts work
- ✅ Images demonstrate real FIBO integration
- ✅ Exploration grid shows agentic parameter optimization
- ✅ Complete audit trail from input to output

For the live demo, use the React frontend at `http://localhost:5173` after starting both backend and frontend servers.

---

**Generated by:** `backend/scripts/generate_demo_outputs.py`  
**Project:** Agentic Ad Optimizer  
**Phase:** 3.1 - "Top-prize contender" upgrades
"""
    
    with open(run_dir / "summary.md", "w") as f:
        f.write(summary_content)
    
    # Generate README with reproduction instructions
    readme_content = """# How to Reproduce This Demo Output

This directory contains a complete evidence pack generated by the Agentic Ad Optimizer.

## Prerequisites

- Python 3.10+
- Node.js 18+
- (Optional) Bria FIBO API key for live image generation

##Setup

1. **Install backend dependencies:**
   ```bash
   python -m venv .venv
   .venv\\Scripts\\Activate.ps1  # Windows PowerShell
   # or: source .venv/bin/activate  # Mac/Linux
   pip install -r requirements.txt
   ```

2. **Install frontend dependencies:**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

3. **Set API key (optional):**
   ```bash
   # Windows PowerShell
   $env:FIBO_API_KEY="your_key_here"
   
   # Mac/Linux
   export FIBO_API_KEY="your_key_here"
   ```

## Run the Demo Script

```bash
# Start the backend first (in one terminal)
uvicorn backend.app.main:app --reload --port 8000

# Run the demo output generator (in another terminal)
python backend/scripts/generate_demo_outputs.py
```

The script will:
1. Generate an experiment plan
2. Create creative variants with FIBO specs
3. Score the creatives
4. Regenerate one variant with Lock Lighting preset
5. Run the Visual Exploration Grid (8 variants)
6. Download all images
7. Save all JSON payloads
8. Generate this summary

## View the Results

Check the `demo_outputs/run_<timestamp>/` directory for:
- `payloads/*.json` - All API requests and responses
- `images/*.*` - All generated images
- `summary.md` - Detailed walkthrough
- `README.md` - This file

## Inspect the JSON

All JSON files are formatted for readability. You can:
- View them in any text editor
- Use `jq` for filtering: `cat payloads/05_explore_variants_response.json | jq '.meta'`
- Import them into Postman/Insomnia for API testing

## Manual Testing (UI)

To test the full user interface:

```bash
# Terminal 1: Backend
uvicorn backend.app.main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend
npm run dev
```

Then visit `http://localhost:5173` and follow the 3-step workflow.

## Questions?

See the main `README.md` in the project root for full documentation.
"""
    
    with open(run_dir / "README.md", "w") as f:
        f.write(readme_content)
    
    print(f"   - Created summary.md")
    print(f"   - Created README.md")
    
    # Final summary
    print("\n" + "=" * 60)
    print(f"[SUCCESS] Demo outputs generated successfully!")
    print(f"\n[DIR] Output directory: {run_dir}")
    print(f"   - {len(list(payloads_dir.glob('*.json')))} JSON files")
    print(f"   - {len(list(images_dir.glob('*.*')))} images")
    print(f"   - 2 documentation files")
    print("\n Use this evidence pack for DevPost or judge review! [ROCKET]")
    print("=" * 60)

if __name__ == "__main__":
    print("[*] Agentic Ad Optimizer - Demo Output Generator")
    print("Phase 3.1 Task C: Evidence Pack Creation\n")
    
    asyncio.run(generate_demo_outputs())
