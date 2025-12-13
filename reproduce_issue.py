import sys
import json
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path("c:/dev/agentic-ad-optimizer")))

from backend.schemas.models import ExperimentPlan

json_content = """{
  "experiment_id": "exp_506",
  "objective": "Increase ROAS",
  "hypothesis": "New creative variants targeting Health-conscious millennials for LunaGlow Sunscreen SPF 50 will outperform control",
  "variants": [
    {
      "variant_id": "A",
      "control": true,
      "description": "Control variant (Generic)"
    },
    {
      "variant_id": "B",
      "control": false,
      "description": "Benefit-focused: LunaGlow Sunscreen SPF 50 saves time"
    },
    {
      "variant_id": "C",
      "control": false,
      "description": "Social Proof: LunaGlow Sunscreen SPF 50 user reviews"
    }
  ],
  "metrics": [
    "ctr",
    "cpc",
    "cvr",
    "roas",
    "net_profit"
  ],
  "sample_size_rules": {
    "min_spend_per_variant": 200.0,
    "min_conversions": 50
  },
  "guardrails": {
    "brand_voice": "Clean, scientific, fresh, premium",
    "avoid_words": [
      "chemical",
      "sticky",
      "cheap"
    ],
    "required_terms": [
      "dermatologist-tested",
      "reef-safe"
    ],
    "disclaimer": "Reapply every 2 hours.",
    "prohibited_claims": [
      "100% sun block",
      "waterproof (must say water resistant)"
    ],
    "regulated_category": "health",
    "target_channel": "Meta"
  }
}"""

try:
    plan = ExperimentPlan.model_validate_json(json_content)
    print("✅ Validation Successful")
except Exception as e:
    print(f"❌ Validation Failed: {e}")
