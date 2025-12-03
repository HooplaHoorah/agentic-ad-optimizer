import os
import random
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from ..schemas.models import (
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
        default_spec: Dict[str, Any] = {
            "camera_angle": "medium",
            "shot_type": "product_only",
            "lighting_style": "warm",
            "color_palette": "pastel",
            "background_type": "studio",
        }
        try:
            result = generate_fibo_image(default_spec, f"{creative.hook} {creative.headline}")
            creative.image_url = result.image_url
            creative.fibo_spec = result.resolved_spec
            # Mark whether we hit the real API or are in mock mode
            creative.image_status = "fibo" if os.getenv("FIBO_API_KEY") else "mocked"
        except Exception as e:
            # Log the issue and attach fallback image
            creative.image_url = "https://placehold.co/600x400/png?text=Error"
            creative.fibo_spec = default_spec
            creative.image_status = "error"
        creatives.append(creative)
    return creatives


@app.post("/score-creatives", response_model=list[RubricScore])
def evaluate_creatives(creatives: list[CreativeVariant]):
    """Assign dummy rubric scores to creatives."""
    scores: list[RubricScore] = []
    for creative in creatives:
        # Randomize scores slightly
        clarity = random.randint(3, 5)
        emotional = random.randint(2, 5)

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


class RegenerateRequest(BaseModel):
    """Request model for regenerating a FIBO image."""

    variant: CreativeVariant
    patch: Dict[str, Any]


@app.post("/regenerate-image", response_model=CreativeVariant)
def regenerate_image(req: RegenerateRequest) -> CreativeVariant:
    """Regenerate a FIBO image based on a patch to the existing spec.

    Merges the incoming patch into the variant's existing `fibo_spec` and
    delegates to the FIBO client.  If the FIBO API key is not set, the call
    is performed in mock mode and a deterministic placeholder is returned.
    """
    base_spec: Dict[str, Any] = req.variant.fibo_spec or {}
    # Merge the existing spec with the user‑supplied patch (patch values override)
    merged_spec = {**base_spec, **req.patch}
    try:
        result = generate_fibo_image(merged_spec, f"{req.variant.hook} {req.variant.headline}")
        req.variant.image_url = result.image_url
        req.variant.fibo_spec = result.resolved_spec
        req.variant.image_status = "fibo" if os.getenv("FIBO_API_KEY") else "mocked"
    except Exception:
        # On error, leave the existing image URL but update the spec anyway
        req.variant.fibo_spec = merged_spec
        req.variant.image_status = "error"
    return req.variant
