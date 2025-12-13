import os
from dotenv import load_dotenv

load_dotenv()
import random
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.schemas.models import (
    BusinessSnapshot,
    ExperimentPlan,
    VariantPlan,
    SampleSizeRules,
    CreativeVariant,
    RubricScore,
    ExperimentResult,
    VariantResult,
    NextTestRecommendation,
)
from pydantic import BaseModel
from typing import Dict, Any

from .fibo_client import generate_fibo_image


app = FastAPI(title="Agentic Ad Optimizer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "Welcome to the Agentic Ad Optimizer API"}


@app.post("/experiment-plan", response_model=ExperimentPlan)
def create_experiment_plan(snapshot: BusinessSnapshot):
    """Generate a simple experiment plan from a business snapshot."""
    # Use product name if available
    product_name = snapshot.products[0].name if snapshot.products else "Product"
    audience = snapshot.audiences[0].segment if snapshot.audiences else "General Audience"

    plan = ExperimentPlan(
        experiment_id=f"exp_{random.randint(100, 999)}",
        objective="Increase ROAS",
        hypothesis=f"New creative variants targeting {audience} for {product_name} will outperform control",
        variants=[
            VariantPlan(variant_id="A", control=True, description="Control variant (Generic)"),
            VariantPlan(
                variant_id="B", control=False, description=f"Benefit-focused: {product_name} saves time"
            ),
            VariantPlan(
                variant_id="C", control=False, description=f"Social Proof: {product_name} user reviews"
            ),
        ],
        metrics=["ctr", "cpc", "cvr", "roas", "net_profit"],
        sample_size_rules=SampleSizeRules(
            min_spend_per_variant=200.0,
            min_conversions=50,
        ),
    )
    return plan


@app.post("/creative-variants", response_model=list[CreativeVariant])
def generate_creative_variants(plan: ExperimentPlan):
    """Generate dummy creative variants for each variant in an experiment plan and attach FIBO images."""
    creatives: list[CreativeVariant] = []

    templates: Dict[str, Dict[str, str]] = {
        "A": {"hook": "Stop scrolling!", "headline": "The best solution."},
        "B": {"hook": "Tired of wasting time?", "headline": "Save hours every day."},
        "C": {
            "hook": "See what everyone is talking about.",
            "headline": "Rated 5 stars by thousands.",
        },
    }

    for variant in plan.variants:
        # Simple template selection based on variant ID suffix or random
        vid = variant.variant_id[-1] if variant.variant_id else "A"
        template = templates.get(
            vid, {"hook": f"Discover {variant.description}", "headline": "Learn More"}
        )

        creative = CreativeVariant(
            variant_id=variant.variant_id,
            hook=template["hook"],
            primary_text=f"Experience the difference with our latest offering. {variant.description}.",
            headline=template["headline"],
            call_to_action="Shop Now",
        )

        # Build a default image spec keyed off the experiment plan; real logic could
        # incorporate channel, audience and product attributes.  Here we keep it
        # simple and deterministic.
               # Create a base spec and adjust based on variant description
        spec: Dict[str, Any] = {
            "camera_angle": "medium",
            "shot_type": "product_only",
            "lighting_style": "warm",
            "color_palette": random.choice(["pastel", "vibrant", "neutral"]),
            "background_type": "studio",
        }
        desc_lower = variant.description.lower()
        if "benefit" in desc_lower or "saves time" in desc_lower:
            spec["shot_type"] = "product_in_use"
            spec["background_type"] = "lifestyle"
            spec["lighting_style"] = "bright"
        elif "social proof" in desc_lower or "user reviews" in desc_lower:
            spec["shot_type"] = "people_with_product"
            spec["background_type"] = "testimonial"
            spec["lighting_style"] = "neutral" 
        try:
            result = generate_fibo_image(spec, f"{creative.hook} {creative.headline}")
            creative.image_url = result.image_url
            creative.fibo_spec = result.resolved_spec
            # Mark whether we hit the real API or are in mock mode
            creative.image_status = "fibo" if os.getenv("FIBO_API_KEY") else "mocked"
        except Exception as e:
            # Log the issue and attach fallback image
            creative.image_url = "https://placehold.co/600x400/png?text=Error"
            creative.fibo_spec = spec
            creative.image_status = "error"
        creatives.append(creative)
    return creatives


@app.post("/score-creatives", response_model=list[RubricScore])
def evaluate_creatives(creatives: list[CreativeVariant]):
    """Assign heuristic rubric scores to creatives based on FIBO image specs."""
    scores: list[RubricScore] = []
    for creative in creatives:
        # Compute baseline clarity and emotional scores based on FIBO spec
        # Start with random base values in a moderate range
        clarity = random.uniform(3, 5)
        emotional = random.uniform(2, 5)
        spec = getattr(creative, "fibo_spec", {}) or {}
        shot = spec.get("shot_type")
        palette = spec.get("color_palette")
        # Adjust clarity based on shot type: product_only images are clearer, people_with_product less so
        if shot == "product_only":
            clarity += 2
        elif shot == "product_in_use":
            clarity += 1
        elif shot == "people_with_product":
            clarity -= 1
        # Adjust emotional resonance: people in the shot and vibrant colors boost emotional appeal
        if shot == "people_with_product":
            emotional += 2
        if palette == "vibrant":
            emotional += 1
        elif palette == "neutral":
            clarity += 1
        # Penalize scores if image generation failed
        if getattr(creative, "image_status", "") == "error":
            clarity = 0
            emotional = 0
        
        scores.append(
            RubricScore(
                creative_id=creative.variant_id,
                clarity_of_promise=clarity,
                emotional_resonance=emotional,
                proof_and_credibility=random.randint(3, 5),
                offer_and_risk_reversal=random.randint(3, 5),
                call_to_action_score=random.randint(3, 5),
                channel_fit=random.randint(3, 5),
                curiosity_hook_factor=random.randint(2, 5),
                overall_strength=(clarity + emotional) / 2 + 0.5,  # Dummy calculation
                feedback=
                f"Good clarity ({clarity}). Consider improving emotional resonance."
                if emotional < 4
                else "Strong emotional appeal!",
            )
        )
    return scores


@app.post("/results", response_model=NextTestRecommendation)
def process_experiment_results(results: ExperimentResult):
    """Process experiment results and suggest next tests."""
    if not results.results:
        raise HTTPException(status_code=400, detail="No results provided")
    # determine winner by highest profit
    winner = max(results.results, key=lambda r: r.profit)

    recommendation = NextTestRecommendation(
        experiment_id=results.experiment_id,
        recommended_variants=[
            VariantPlan(variant_id="D", control=False, description=f"Iterate on {winner.variant_id} - Angle 1"),
            VariantPlan(variant_id="E", control=False, description=f"Iterate on {winner.variant_id} - Angle 2"),
        ],
        summary=f"Variant {winner.variant_id} was the clear winner with ${winner.profit} profit. "
        "We recommend iterating on its successful elements.",
    )
    return recommendation


class SpecPatch(BaseModel):
    """Explicit fields for a FIBO image spec patch.
    All fields are optional because the client may only override a subset.
    """
    camera_angle: str | None = None
    shot_type: str | None = None
    lighting_style: str | None = None
    color_palette: str | None = None
    background_type: str | None = None
    prompt: str | None = None

class RegenerateRequest(BaseModel):
    """Request model for regenerating a FIBO image.
    It contains the creative variant to update and a spec patch with the fields above.
    """
    variant: CreativeVariant
    spec_patch: SpecPatch

# Updated endpoint to use the new model and log actions
@app.post("/regenerate-image", response_model=CreativeVariant)
def regenerate_image(req: RegenerateRequest) -> CreativeVariant:
    """Regenerate a FIBO image based on a patch to the existing spec.
    The incoming patch overrides the existing `fibo_spec`. The endpoint returns the updated creative.
    """
    # Merge the existing spec with the user‑supplied patch (patch values override)
    base_spec: Dict[str, Any] = req.variant.fibo_spec or {}
    # Convert SpecPatch to dict, excluding None values
    patch_dict = req.spec_patch.dict(exclude_unset=True)
    merged_spec = {**base_spec, **patch_dict}
    try:
        result = generate_fibo_image(merged_spec, f"{req.variant.hook} {req.variant.headline}")
        req.variant.image_url = result.image_url
        req.variant.fibo_spec = result.resolved_spec
        req.variant.image_status = "fibo" if os.getenv("FIBO_API_KEY") else "mocked"
        # Log concise info (no secrets)
        print(f"regenerate-image creative_id={req.variant.variant_id} status={req.variant.image_status}")
    except Exception as e:
        # On error, keep existing image URL but update the spec anyway
        req.variant.fibo_spec = merged_spec
        req.variant.image_status = "error"
        print(f"regenerate-image creative_id={req.variant.variant_id} status=error error={str(e)}")
    return req.variant


# Phase 3.1 Task B: Visual Exploration Grid (8 variants)
class ExploreVariantsRequest(BaseModel):
    """Request model for exploring visual variants of a creative."""
    base_variant: CreativeVariant
    axes: Dict[str, list[str]] = {
        "lighting_style": ["warm", "cool"],
        "color_palette": ["warm_golden", "pastel"],
        "background_type": ["studio", "natural"]
    }


class ExploreVariantsResponse(BaseModel):
    """Response model containing the grid of explored variants."""
    base_variant_id: str
    generated: list[CreativeVariant]
    meta: Dict[str, Any]


@app.post("/explore-variants", response_model=ExploreVariantsResponse)
def explore_variants(req: ExploreVariantsRequest) -> ExploreVariantsResponse:
    """Generate 8 visual variants by exploring combinations of FIBO parameters.
    
    This endpoint creates a cartesian product of the specified axes
    (lighting_style, color_palette, background_type) to demonstrate
    agentic exploration of the FIBO JSON parameter space.
    """
    import time
    from itertools import product
    
    start_time = time.time()
    generated_variants: list[CreativeVariant] = []
    
    # Extract axis values
    lighting_styles = req.axes.get("lighting_style", ["warm", "cool"])
    color_palettes = req.axes.get("color_palette", ["warm_golden", "pastel"])
    background_types = req.axes.get("background_type", ["studio", "natural"])
    
    # Generate cartesian product (2 x 2 x 2 = 8 combinations)
    combinations = list(product(lighting_styles, color_palettes, background_types))
    
    for idx, (lighting, palette, background) in enumerate(combinations):
        # Create a spec patch with these specific values
        spec_patch = SpecPatch(
            lighting_style=lighting,
            color_palette=palette,
            background_type=background
        )
        
        # Create a copy of the base variant
        variant_copy = req.base_variant.copy(deep=True)
        variant_copy.variant_id = f"{req.base_variant.variant_id}_explore_{idx+1}"
        
        # Apply the regeneration logic (same as regenerate_image endpoint)
        base_spec: Dict[str, Any] = variant_copy.fibo_spec or {}
        patch_dict = spec_patch.dict(exclude_unset=True)
        merged_spec = {**base_spec, **patch_dict}
        
        try:
            result = generate_fibo_image(merged_spec, f"{variant_copy.hook} {variant_copy.headline}")
            variant_copy.image_url = result.image_url
            variant_copy.fibo_spec = result.resolved_spec
            variant_copy.image_status = "fibo" if os.getenv("FIBO_API_KEY") else "mocked"
            print(f"explore-variants generated variant {idx+1}: lighting={lighting}, palette={palette}, background={background}, status={variant_copy.image_status}")
        except Exception as e:
            variant_copy.fibo_spec = merged_spec
            variant_copy.image_status = "error"
            print(f"explore-variants variant {idx+1} error: {str(e)}")
        
        generated_variants.append(variant_copy)
    
    runtime_ms = int((time.time() - start_time) * 1000)
    
    return ExploreVariantsResponse(
        base_variant_id=req.base_variant.variant_id,
        generated=generated_variants,
        meta={
            "count": len(generated_variants),
            "runtime_ms": runtime_ms,
            "axes_explored": {
                "lighting_style": lighting_styles,
                "color_palette": color_palettes,
                "background_type": background_types
            }
        }
    )
