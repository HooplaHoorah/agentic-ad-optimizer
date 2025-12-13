e# API Contracts

This document describes the request and response schemas for the Agentic Ad Optimizer API endpoints implemented in the FastAPI backend. These contracts align with the Pydantic models defined in `backend/schemas/models.py`.

## Root endpoint

**GET /**  
Returns a simple JSON message confirming the API is reachable.

Example response:
```
{"message": "Welcome to the Agentic Ad Optimizer API"}
```

## Generate Experiment Plan

**POST /experiment-plan**

Generates a basic experiment plan from a business snapshot.

### Request body (BusinessSnapshot)
- `products`: array of product objects, each with:
  - `id`: string identifier
  - `name`: product name
  - `price`: price of the product (float)
  - `margin`: optional profit margin
  - `category`: optional category
  - `benefits`: optional list of benefit strings
  - `objections`: optional list of customer objections
- `audiences`: array of audience objects, each with:
  - `segment`: audience segment name
  - `pain_points`: optional list of pain points
  - `jobs_to_be_done`: optional list of jobs to be done
- `historical_performance`: array of historical performance records, each with:
  - `channel`: channel name
  - `impressions`: number of impressions (int)
  - `clicks`: number of clicks (int)
  - `conversions`: number of conversions (int)
  - `spend`: advertising spend (float)
  - `revenue`: revenue generated (float)
- `sales_data`: optional list of arbitrary key/value pairs representing additional sales metrics.

### Response body (ExperimentPlan)
- `experiment_id`: string identifier for the experiment
- `objective`: primary objective of the experiment
- `hypothesis`: hypothesis being tested
- `variants`: array of `VariantPlan` objects:
  - `variant_id`: identifier (e.g., "A", "B")
  - `control`: boolean indicating if this is the control variant
  - `description`: description of the creative idea
- `metrics`: array of metric names to track (e.g., "ctr", "roas")
- `sample_size_rules`: object defining minimum thresholds:
  - `min_spend_per_variant`: minimum spend per variant (float)
  - `min_conversions`: minimum number of conversions (int)

## Generate Creative Variants

**POST /creative-variants**

Generates creative variants for the variants defined in an experiment plan.

### Request body (ExperimentPlan)
An `ExperimentPlan` as returned from `/experiment-plan` (see above).

### Response body (list[CreativeVariant])
A list of creative variants corresponding to each variant in the plan:
- `variant_id`: identifier of the variant
- `hook`: short hook or tagline
- `primary_text`: main ad copy
- `headline`: ad headline
- `call_to_action`: call to action text (e.g., "Buy Now")

- `image_url`: URL of the generated FIBO image (string). When no FIBO API key is configured, this will be a placeholder image.
- `fibo_spec`: object representing the `FiboImageSpec` used to generate the image (e.g., structured prompt, mood, style).
 - `- `image_status`: status of image generation (string; one of `"fibo"`, `"mocked"`, or `"error"`). A value of `"fibo"` means the image was generated using Bria's FIBO API; `"mocked"` means a deterministic placeholder was used; `"error"` indicates that image generation failed.
- 
## Regenerate Image

**POST /regenerate-image**

Regenerates the FIBO image for an existing creative using a partial update to the FiboImageSpec.

### Request body (RegenerateRequest)
- - `variant`: the full CreativeVariant object for the creative you want to regenerate. The backend uses this object to merge its existing `fibo_spec` with the provided patch.
- `spec_patch`: a partial FiboImageSpec object containing only the fields you want to override (e.g. `camera_angle`, `shot_type`, `lighting_style`, `color_palette`, `background_type`, `prompt`). Only provided fields are merged into the existing spwill be merged into the existing spec.

### Response body (CreativeVariant)
Returns the updated creative variant with new `image_url`, updated `fibo_spec`, and `image_status` fields. See the CreativeVariant response above for field descriptions.
 `

**POST /score-creatives**

Assigns rubric scores to the provided creative variants.

### Request body (list[CreativeVariant])
A list of creative variant objects (see above) to be evaluated.

### Response body (list[RubricScore])
A list of rubric score objects, one per creative:
- `creative_id`: the identifier of the creative being scored
- `clarity_of_promise`: integer score reflecting how clearly the promise is articulated
- `emotional_resonance`: integer score for emotional connection
- `proof_and_credibility`: integer score for evidence and credibility
- `offer_and_risk_reversal`: integer score for attractiveness of the offer and risk reversal
- `call_to_action_score`: integer score for the strength of the call to action
- `channel_fit`: integer score for how well the creative fits the chosen channel
- `curiosity_hook_factor`: integer score for how well the hook builds curiosity
- `overall_strength`: float representing the overall weighted strength
- `feedback`: textual feedback explaining the scores

## Process Experiment Results

**POST /results**

Processes the results of an experiment and recommends next tests.

### Request body (ExperimentResult)
- `experiment_id`: identifier of the experiment
- `results`: array of `VariantResult` objects, each with:
  - `variant_id`: identifier
  - `impressions`: number of impressions (int)
  - `clicks`: number of clicks (int)
  - `spend`: total spend (float)
  - `conversions`: number of conversions (int)
  - `revenue`: revenue generated (float)
  - `profit`: profit generated (float)
  - `cac`: customer acquisition cost (float)
  - `roas`: return on ad spend (float)
- `winner_variant_id`: the variant that won according to some metric

### Response body (NextTestRecommendation)
- `experiment_id`: same ID as the input
- `recommended_variants`: array of new `VariantPlan` objects representing the next test variants
- `summary`: textual summary explaining why the recommendation was made
