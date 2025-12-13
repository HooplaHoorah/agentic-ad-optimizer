# Demo Outputs - Evidence Pack

This directory contains evidence of FIBO controllability and the application's agentic optimization capabilities, serving as **backup proof** if the live application cannot be run.

## Purpose

Even if a judge cannot run the application (due to API keys, environment issues, or time constraints), this evidence pack demonstrates:
- How the agent uses FIBO parameters to control image generation
- The "agentic loop" of experimentation and optimization  
- Before/after regeneration with explicit spec changes

##Files Included

### 1. Spec Patch JSON Files

These files show **exactly** what parameters the agent can modify when regenerating images.

#### `product_shot.json`
- **Changed:** `lighting_style` → `"soft"`, `background_type` → `"studio"`, `shot_type` → `"product_only"`
- **Got:** Professional, clean imagery ideal for e-commerce listings
- **Impact:** Higher clarity scores, minimal distractions, professional appearance

#### `lifestyle.json`
- **Changed:** `lighting_style` → `"warm"`, `background_type` → `"lifestyle"`, `shot_type` → `"product_in_use"`
- **Got:** Warm, relatable imagery showing product in real-world context
- **Impact:** Higher emotional resonance, contextual appeal, human connection

#### `punchy_ad.json`
- **Changed:** `lighting_style` → `"dramatic"`, `color_palette` → `"vibrant"`, `camera_angle` → `"close"`
- **Got:** Bold, attention-grabbing advertisement with high visual impact
- **Impact:** Increased curiosity hook factor, scroll-stopping creative, strong brand presence

### 2. Screenshots (recommended)

To provide visual proof, include 2-6 screenshots showing:

1. **LIVE Badge** - Demonstrating successful FIBO API integration
2. **Preset Buttons** - Product Shot / Lifestyle / Punchy Ad interface
3. **Before/After Panel** - Regenerated image comparison with timestamps
4. **Network Tab** - API request/response showing spec_patch structure
5. **Score Breakdown** - How different specs affect rubric scores
6. **Agentic Loop** - Winner selection and next test recommendation

## How It Works: Agentic FIBO Optimization

### Step 1: Generate Initial Variants
The agent creates 3 creative variants (A, B, C) with different messaging angles:
- Variant A: Generic/Control
- Variant B: Benefit-focused  
- Variant C: Social proof

Each variant gets a FIBO-generated image with an initial `fibo_spec` based on the variant's description.

### Step 2: Interactive Regeneration
Users can regenerate any variant's image by either:
- **Selecting a preset** (Product Shot, Lifestyle, Punchy Ad)
- **Typing a custom prompt** with FIBO parameters

The app sends a `spec_patch` to `/regenerate-image` which **merges** the patch with the existing spec:

```json
{
  "variant": { /* full variant object */ },
  "spec_patch": {
    "prompt": "Lifestyle photography, warm natural lighting",
    "lighting_style": "warm",
    "background_type": "lifestyle"
  }
}
```

### Step 3: Score & Optimize
The backend scores each creative across 8 dimensions:
- Clarity of promise
- Emotional resonance
- Proof and credibility
- Offer and risk reversal
- Call to action strength
- Channel fit
- Curiosity hook factor
- Overall strength

**Key:** FIBO spec parameters directly influence these scores:
- `shot_type: "product_only"` → +2 clarity
- `shot_type: "people_with_product"` → +2 emotional resonance
- `color_palette: "vibrant"` → +1 emotional resonance
-`lighting_style: "dramatic"` → higher curiosity hook

### Step 4: Identify Winner & Recommend Next Test
After scoring, the agent:
1. Identifies the winning variant (highest profit/ROAS)
2. Analyzes what FIBO parameters contributed to its success
3. Suggests 2 follow-up variants to test with refined FIBO specs

**Example Output:**
```
Winner: Variant B (lifestyle shot, warm lighting)
Profit: $1,200
Next test: Try warmer lighting + tighter product crop for even higher clarity
```

## The Agentic Difference

Traditional A/B testing: "Which creative won?"  
**Agentic optimization:** "Why did it win, and what should we test next based on visual parameters?"

This application continuously improves by:
- Testing visual hypotheses (lighting, composition, framing)
- Learning from FIBO-driven variants
- Recommending data-driven next tests
- Closing the loop between creative performance and visual parameters

## For Judges: Quick Verification

If you can run the app:
1. Select a Campaign Template (e.g., "SaaS - FlowPilot")
2. Generate creatives
3. Try each preset on different variants
4. Observe before/after thumbnails
5. Score and see how specs affect rubric scores
6. Export the full artifact bundle

If you cannot run the app:
- Review these spec patch files
- See screenshots/ for visual proof
- Read the spec_patch → outcome correlation above

## Technical Details

- **Backend:** FastAPI with explicit `SpecPatch` Pydantic model
- **FIBO Integration:** `fibo_spec` merged with `spec_patch` on each regeneration
- **Image Status:** "fibo" (live API), "mocked" (no key), or "error" (failed)
- **Logging:** Concise one-line logs per regeneration (no secrets)
- **Export:** Full JSON bundle with plan, variants, scores, recommendation

---

**Questions?** See main README.md for setup instructions and troubleshooting. This evidence pack ensures the hackathon submission is judge-proof even without a live demo.  
