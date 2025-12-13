"""
Final Demo Run: LunaGlow Sunscreen Campaign

This script runs a complete agentic loop for a distinct campaign (DTC E-commerce)
and saves all artifacts to the 'FinalDemo' folder as requested.
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

from backend.schemas.models import BusinessSnapshot

# Configuration
API_BASE = "http://localhost:8000"
OUTPUT_BASE = Path("FinalDemo")

async def run_final_demo():
    """Run the LunaGlow demo scenario and save artifacts."""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = OUTPUT_BASE / f"run_{timestamp}"
    payloads_dir = run_dir / "payloads"
    images_dir = run_dir / "images"
    
    # Create directories
    run_dir.mkdir(parents=True, exist_ok=True)
    payloads_dir.mkdir(exist_ok=True)
    images_dir.mkdir(exist_ok=True)
    
    print(f"📦 Generating Final Demo outputs in: {run_dir}")
    print("=" * 60)
    
    async with httpx.AsyncClient(timeout=180.0) as client:
        
        async def safe_request(method, url, **kwargs):
            try:
                response = await client.request(method, url, **kwargs)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                print(f"\n❌ Request failed: {method} {url}")
                if 'response' in locals():
                    print(f"Response: {response.text[:500]}...")
                    with open("last_error.txt", "w") as f:
                        f.write(response.text)
                raise e

        # Step 1: Generate Plan (LunaGlow Sunscreen)
        print("\n1️⃣  Generating experiment plan (LunaGlow)...")

        snapshot_data = {
            "products": [{
                "id": "product_luna",
                "name": "LunaGlow Sunscreen SPF 50",
                "price": 32.0,
                "margin": 65.0,
                "category": "Beauty/Health",
                "benefits": ["Reef-safe", "Non-greasy", "No white cast", "Hydrating"],
                "objections": ["Price point", "Greasy feel"]
            }],
            "audiences": [{
                "id": "audience_millennial",
                "segment": "Health-conscious millennials",
                "size_estimate": 1200000.0,
                "platform": "Instagram",
                "pain_points": ["Chemical sunscreens", "Sticky residue", " harming coral reefs"],
                "jobs_to_be_done": ["Protect skin", "Look good at the beach", "Be eco-friendly"]
            }],
            "guardrails": {
                "brand_voice": "Clean, scientific, fresh, premium",
                "avoid_words": ["chemical", "sticky", "cheap"],
                "required_terms": ["dermatologist-tested", "reef-safe"],
                "disclaimer": "Reapply every 2 hours.",
                "prohibited_claims": ["100% sun block", "waterproof (must say water resistant)"],
                "regulated_category": "health",
                "target_channel": "Meta"
            },
            "historical_performance": [],
            "sales_data": []
        }
        
        # Save request
        with open(payloads_dir / "01_experiment_plan_request.json", "w") as f:
            json.dump(snapshot_data, f, indent=2)
        
        plan = await safe_request("POST", f"{API_BASE}/experiment-plan", json=snapshot_data)
        
        # Save response
        with open(payloads_dir / "01_experiment_plan_response.json", "w") as f:
            json.dump(plan, f, indent=2)
        
        print(f"   ✓ Plan created: {plan['experiment_id']}")
        print(f"   ✓ Variants: {', '.join([v['variant_id'] for v in plan['variants']])}")
        
        # Step 2: Generate Creatives
        print("\n2️⃣  Generating creative variants...")
        creatives = await safe_request("POST", f"{API_BASE}/creative-variants", json=plan)
        
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
                    print(f"   ⚠️  Could not download image: {e}")
        
        # Step 3: Score Creatives
        print("\n3️⃣  Scoring creative variants...")
        scores = await safe_request("POST", f"{API_BASE}/score-creatives", json=creatives)
        
        with open(payloads_dir / "03_score_creatives_response.json", "w") as f:
            json.dump(scores, f, indent=2)
        
        print(f"   ✓ Scored {len(scores)} creatives")
        
        # Step 4: Regenerate with Preset (Variant B)
        print("\n4️⃣  Testing Regeneration (Lock Lighting / Golden Hour)...")
        variant_b = next((c for c in creatives if c["variant_id"] == "B"), None)
        
        if variant_b:
            regenerate_req = {
                "variant": variant_b,
                "spec_patch": {
                    "lighting_style": "warm",
                    "color_palette": "warm_golden",
                    "prompt": "Same product placement, but with warm golden hour beach sunlight"
                }
            }
            
            with open(payloads_dir / "04_regenerate_request.json", "w") as f:
                json.dump(regenerate_req, f, indent=2)
            
            regenerated = await safe_request("POST", f"{API_BASE}/regenerate-image", json=regenerate_req)
            
            with open(payloads_dir / "04_regenerate_response.json", "w") as f:
                json.dump(regenerated, f, indent=2)
            
            print(f"   ✓ Regenerated Variant B with Golden Hour lighting")
            
            if regenerated.get("image_url"):
                try:
                    img_response = await client.get(regenerated["image_url"])
                    if img_response.status_code == 200:
                        ext = "png" if "png" in regenerated["image_url"] else "jpg"
                        img_path = images_dir / f"creative_B_regenerated.{ext}"
                        with open(img_path, "wb") as f:
                            f.write(img_response.content)
                        print(f"   ✓ Downloaded regenerated image")
                except Exception as e:
                    print(f"   ⚠️  Could not download regenerated image: {e}")

        # Step 5: Visual Exploration (Standard)
        print("\n5️⃣  Running Standard Visual Exploration (8 variants)...")
        if variant_b:
            explore_req = {
                "base_variant": variant_b,
                "axes": {
                    "lighting_style": ["warm", "cool"],
                    "color_palette": ["warm_golden", "pastel"],
                    "background_type": ["studio", "natural"]
                }
            }
            
            with open(payloads_dir / "05_explore_standard_request.json", "w") as f:
                json.dump(explore_req, f, indent=2)
            
            exploration = await safe_request("POST", f"{API_BASE}/explore-variants", json=explore_req)
            
            with open(payloads_dir / "05_explore_standard_response.json", "w") as f:
                json.dump(exploration, f, indent=2)
            
            print(f"   ✓ Generated {exploration['meta']['count']} explored variants")
            
             # Download explored variant images
            for idx, explored in enumerate(exploration["generated"], 1):
                if explored.get("image_url"):
                    try:
                        img_response = await client.get(explored["image_url"])
                        if img_response.status_code == 200:
                            ext = "png" if "png" in explored["image_url"] else "jpg"
                            img_path = images_dir / f"explored_std_{idx:02d}.{ext}"
                            with open(img_path, "wb") as f:
                                f.write(img_response.content)
                    except Exception as e:
                        pass

        # Step 5b: Visual Exploration (Advanced)
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
            
            with open(payloads_dir / "05b_explore_advanced_request.json", "w") as f:
                json.dump(explore_adv_req, f, indent=2)
            
            adv_exploration = await safe_request("POST", f"{API_BASE}/explore-variants", json=explore_adv_req)
            
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
                            img_path = images_dir / f"explored_adv_{idx:02d}.{ext}"
                            with open(img_path, "wb") as f:
                                f.write(img_response.content)
                    except Exception as e:
                        pass

    # Summary Markdown
    summary_content = f"""# Final Demo: LunaGlow Sunscreen
**Run ID:** {run_dir.name}
**Date:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Product:** LunaGlow Sunscreen SPF 50 ({snapshot_data['products'][0]['category']})

## Artifacts Created
- **Experiment Plan:** `payloads/01_experiment_plan_response.json`
- **Creative Variants:** `payloads/02_creative_variants_response.json`
- **Scores:** `payloads/03_score_creatives_response.json`
- **Regenerated Image:** `images/creative_B_regenerated.png` (Golden Hour preset)
- **Standard Exploration:** `images/explored_std_*.png` (Lighting/Palette/BG)
- **Advanced Exploration:** `images/explored_adv_*.png` (Shot Type/Camera Angle/Lighting)

## Scenario
This demo proves the system handles diverse verticals (Beauty/DTC) with specific guardrails:
- **Avoid:** {', '.join(snapshot_data['guardrails']['avoid_words'])}
- **Require:** {', '.join(snapshot_data['guardrails']['required_terms'])}
"""
    with open(run_dir / "summary.md", "w") as f:
        f.write(summary_content)

    print("\n" + "=" * 60)
    print(f"[SUCCESS] Final Demo loop complete. Artifacts in: {run_dir}")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(run_final_demo())
