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
    Guardrails,
)
from pydantic import BaseModel
from typing import Dict, Any, List, Optional

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


@app.get("/health")
def health_check():
    """Health check endpoint to confirm backend is online and check FIBO mode."""
    is_live = bool(os.getenv("FIBO_API_KEY"))
    return {
        "status": "ok",
        "mode": "live" if is_live else "mocked",
        "fibo_enabled": is_live
    }


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
        guardrails=snapshot.guardrails
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

        primary_text = f"Experience the difference with our latest offering. {variant.description}."
        
        # Apply Guardrails - Enforce by default (Task A1)
        guardrails_report = {"status": "pass", "issues": []}
        if plan.guardrails:
            # 1. Append disclaimer if missing
            if plan.guardrails.disclaimer and plan.guardrails.disclaimer not in primary_text:
                primary_text += f" {plan.guardrails.disclaimer}"

            # 2. Append required terms if missing (Task A1)
            # Check combined text blob
            text_blob = (primary_text + " " + template["headline"] + " " + template["hook"]).lower()
            for term in plan.guardrails.required_terms:
                if term and term.lower() not in text_blob:
                    # Satisfy requirement by appending to primary text
                    primary_text += f" {term}."
                    # Update text_blob for subsequent checks
                    text_blob = (primary_text + " " + template["headline"] + " " + template["hook"]).lower()

            # 3. Validation Check (Double check)
            # Check avoid words
            for word in plan.guardrails.avoid_words:
                if word and word.lower() in text_blob:
                    guardrails_report["status"] = "needs_fix"
                    guardrails_report["issues"].append(f"Avoided word found: '{word}'")
            
            # Check required terms again (should be safe now, but good to verify)
            for term in plan.guardrails.required_terms:
                if term and term.lower() not in text_blob:
                     guardrails_report["status"] = "needs_fix"
                     guardrails_report["issues"].append(f"Missing required term: '{term}'")

        creative = CreativeVariant(
            variant_id=variant.variant_id,
            hook=template["hook"],
            primary_text=primary_text,
            headline=template["headline"],
            call_to_action="Shop Now",
            guardrails_report=guardrails_report
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
    try:
        scores: list[RubricScore] = []
        for creative in creatives:
            # Compute baseline clarity and emotional scores based on FIBO spec
            # Start with random base values in a moderate range
            clarity = random.uniform(3, 5)
            emotional = random.uniform(2, 5)
            spec = getattr(creative, "fibo_spec", {}) or {}
            shot = spec.get("shot_type")
            palette = spec.get("color_palette")
            
            # Adjust clarity based on shot type
            if shot == "product_only":
                clarity += 2
            elif shot == "product_in_use":
                clarity += 1
            elif shot == "people_with_product":
                clarity -= 1
                
            # Adjust emotional resonance
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
                    clarity_of_promise=int(clarity),
                    emotional_resonance=int(emotional),
                    proof_and_credibility=random.randint(3, 5),
                    offer_and_risk_reversal=random.randint(3, 5),
                    call_to_action_score=random.randint(3, 5),
                    channel_fit=random.randint(3, 5),
                    curiosity_hook_factor=random.randint(2, 5),
                    overall_strength=(clarity + emotional) / 2 + 0.5,
                    feedback=f"Good clarity ({int(clarity)}). Consider improving emotional resonance." if emotional < 4 else "Strong emotional appeal!",
                )
            )
        return scores
    except Exception as e:
        import traceback
        with open("backend_error.log", "w") as f:
            f.write(str(e) + "\n")
            traceback.print_exc(file=f)
        raise e


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
    """Generate visual variants by exploring combinations of FIBO parameters.
    
    This endpoint creates a cartesian product of the specified axes
    (e.g., lighting_style, shot_type, background_type) to demonstrate
    agentic exploration of the FIBO JSON parameter space.
    """
    import time
    from itertools import product
    
    start_time = time.time()
    generated_variants: list[CreativeVariant] = []
    
    # Extract axis keys and value lists dynamically
    # e.g. keys=["lighting_style", "shot_type"], values=[["warm", "cool"], ["closeup", "wide"]]
    keys = list(req.axes.keys())
    value_lists = list(req.axes.values())
    
    # Generate cartesian product
    combinations = list(product(*value_lists))
    
    for idx, combo in enumerate(combinations):
        # Create user-friendly variant ID
        variant_suffix = f"explore_{idx+1}"
        
        # Create spec update dictionary from keys and this combination
        spec_update = dict(zip(keys, combo))
        
        # Create a copy of the base variant
        variant_copy = req.base_variant.copy(deep=True)
        variant_copy.variant_id = f"{req.base_variant.variant_id}_{variant_suffix}"
        
        # Apply the logic (similar to regenerate_image)
        base_spec: Dict[str, Any] = variant_copy.fibo_spec or {}
        merged_spec = {**base_spec, **spec_update}
        
        try:
            # Generate image with new spec
            result = generate_fibo_image(merged_spec, f"{variant_copy.hook} {variant_copy.headline}")
            variant_copy.image_url = result.image_url
            variant_copy.fibo_spec = result.resolved_spec
            variant_copy.image_status = "fibo" if os.getenv("FIBO_API_KEY") else "mocked"
            
            # Log simple status
            print(f"explore-variants {idx+1}/{len(combinations)}: {spec_update} status={variant_copy.image_status}")
            
        except Exception as e:
            variant_copy.fibo_spec = merged_spec
            variant_copy.image_status = "error"
            print(f"explore-variants {idx+1} error: {str(e)}")
        
        generated_variants.append(variant_copy)
    
    runtime_ms = int((time.time() - start_time) * 1000)
    
    return ExploreVariantsResponse(
        base_variant_id=req.base_variant.variant_id,
        generated=generated_variants,
        meta={
            "count": len(generated_variants),
            "runtime_ms": runtime_ms,
            "axes_explored": req.axes
        }
    )


# Task A2: Auto-fix endpoint
class ApplyGuardrailsRequest(BaseModel):
    variant: CreativeVariant
    guardrails: Guardrails

@app.post("/apply-guardrails", response_model=CreativeVariant)
def apply_guardrails(req: ApplyGuardrailsRequest):
    """Auto-fix a creative variant to satisfy guardrails."""
    variant = req.variant.model_copy(deep=True)
    guardrails = req.guardrails
    changed_fields = []
    
    # 1. Append disclaimer if missing
    if guardrails.disclaimer and guardrails.disclaimer not in variant.primary_text:
        variant.primary_text += f" {guardrails.disclaimer}"
        changed_fields.append("primary_text (disclaimer added)")
    
    # 2. Append required terms if missing
    text_blob = (variant.primary_text + " " + variant.headline + " " + variant.hook).lower()
    for term in guardrails.required_terms:
         if term and term.lower() not in text_blob:
             variant.primary_text += f" {term}."
             changed_fields.append(f"primary_text (added '{term}')")
             # Update blob for next check
             text_blob = (variant.primary_text + " " + variant.headline + " " + variant.hook).lower()

    # 3. Sanitize avoid words (simple replacement)
    import re
    for word in guardrails.avoid_words:
        if word:
             pattern = re.compile(re.escape(word), re.IGNORECASE)
             # Check and replace in all text fields
             if pattern.search(variant.primary_text):
                 variant.primary_text = pattern.sub("***", variant.primary_text)
                 changed_fields.append(f"primary_text (censored '{word}')")
             if pattern.search(variant.headline):
                 variant.headline = pattern.sub("***", variant.headline)
                 changed_fields.append(f"headline (censored '{word}')")
             if pattern.search(variant.hook):
                 variant.hook = pattern.sub("***", variant.hook)
                 changed_fields.append(f"hook (censored '{word}')")
    
    # Update report
    variant.guardrails_report = {
        "status": "pass", 
        "issues": [], 
        "fixed_issues": changed_fields
    }
    
    return variant
