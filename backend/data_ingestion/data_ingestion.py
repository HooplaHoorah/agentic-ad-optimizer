"""
Data ingestion utilities.

This module provides simple routines to generate or ingest advertising and business performance data.
For the hackathon, it returns a mocked BusinessSnapshot object with dummy products, audiences and historical performance.
"""

from ..schemas.models import BusinessSnapshot, Product, Audience, HistoricalPerformance

class DataIngestion:
    """Service for ingesting campaign and sales data."""

    def get_business_snapshot(self) -> BusinessSnapshot:
        """Return a mock BusinessSnapshot for demonstration purposes."""
        products = [
            Product(
                id="prod_1",
                name="Sample Product",
                price=19.99,
                margin=10.0,
                category="Example",
                benefits=["Easy to use", "Affordable"],
                objections=["Too simple"],
            ),
        ]
        audiences = [
            Audience(
                segment="Young Adults",
                pain_points=["Time constraints"],
                jobs_to_be_done=["Quick purchase"],
            ),
        ]
        historical = [
            HistoricalPerformance(
                channel="Facebook",
                impressions=10000,
                clicks=500,
                conversions=50,
                spend=1000.0,
                revenue=1500.0,
            ),
            HistoricalPerformance(
                channel="Google",
                impressions=8000,
                clicks=400,
                conversions=40,
                spend=1200.0,
                revenue=1600.0,
            ),
        ]
        return BusinessSnapshot(
            products=products,
            audiences=audiences,
            historical_performance=historical,
        )
