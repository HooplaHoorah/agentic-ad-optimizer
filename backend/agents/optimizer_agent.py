from ..schemas.models import ExperimentResult, NextTestRecommendation, VariantPlan


class OptimizationAgent:
    """
    Agent responsible for analyzing experiment results and recommending next tests.

    This placeholder implementation selects the winner from the provided ExperimentResult
    and proposes a new test variant derived from the winning variant.
    """

    def __init__(self) -> None:
        # Initialize any necessary resources or models here (placeholder)
        pass

    def recommend_next_tests(self, result: ExperimentResult) -> NextTestRecommendation:
        """
        Analyze experiment results and recommend next test variants.

        Args:
            result: ExperimentResult containing performance results for each variant.

        Returns:
            NextTestRecommendation: A recommendation with baseline control variant and a test variant.
        """
        # Use the winner_variant_id from the experiment result as the baseline
        winner_id = result.winner_variant_id

        # Generate a summary explaining why this variant won
        summary = (
            f"Variant {winner_id} showed the best performance based on the provided metrics. "
            "We recommend using it as the control for the next experiment and testing a variation "
            "to further optimize performance."
        )

        # Create a control variant plan referencing the winner
        control_variant = VariantPlan(
            variant_id=winner_id,
            control=True,
            description=f"Control variant based on winning variant {winner_id}"
        )

        # Create a new test variant by appending a suffix to the winner id
        new_variant_id = f"{winner_id}-variant2"
        test_variant = VariantPlan(
            variant_id=new_variant_id,
            control=False,
            description=f"New variant exploring alternative messaging or creative based on {winner_id}"
        )

        recommended_variants = [control_variant, test_variant]

        return NextTestRecommendation(
            experiment_id=result.experiment_id,
            recommended_variants=recommended_variants,
            summary=summary,
        )
