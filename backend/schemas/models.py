from pydantic import BaseModel
from typing import List, Optional, Dict


class Product(BaseModel):
    id: str
    name: str
    price: float
    margin: Optional[float] = None
    category: Optional[str] = None
    benefits: Optional[List[str]] = None
    objections: Optional[List[str]] = None


class Audience(BaseModel):
    segment: str
    pain_points: Optional[List[str]] = None
    jobs_to_be_done: Optional[List[str]] = None


class HistoricalPerformance(BaseModel):
    channel: str
    impressions: int
    clicks: int
    conversions: int
    spend: float
    revenue: float


class BusinessSnapshot(BaseModel):
    products: List[Product]
    audiences: List[Audience]
    historical_performance: List[HistoricalPerformance]
    sales_data: Optional[List[Dict[str, float]]] = None


class VariantPlan(BaseModel):
    variant_id: str
    control: bool = False
    description: str


class SampleSizeRules(BaseModel):
    min_spend_per_variant: float
    min_conversions: int


class ExperimentPlan(BaseModel):
    experiment_id: str
    objective: str
    hypothesis: str
    variants: List[VariantPlan]
    metrics: List[str]
    sample_size_rules: SampleSizeRules


class CreativeVariant(BaseModel):
    variant_id: str
    hook: str
    primary_text: str
    headline: str
    call_to_action: str


class RubricScore(BaseModel):
    creative_id: str
    clarity_of_promise: int
    emotional_resonance: int
    proof_and_credibility: int
    offer_and_risk_reversal: int
    call_to_action_score: int
    channel_fit: int
    curiosity_hook_factor: int
    overall_strength: float
    feedback: str


class VariantResult(BaseModel):
    variant_id: str
    impressions: int
    clicks: int
    spend: float
    conversions: int
    revenue: float
    profit: float
    cac: float
    roas: float


class ExperimentResult(BaseModel):
    experiment_id: str
    results: List[VariantResult]
    winner_variant_id: str


class NextTestRecommendation(BaseModel):
    experiment_id: str
    recommended_variants: List[VariantPlan]
    summary: str
