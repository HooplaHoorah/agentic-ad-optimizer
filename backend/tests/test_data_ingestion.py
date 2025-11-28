import pytest
from ..data_ingestion import DataIngestion
from ..schemas.models import BusinessSnapshot


def test_get_business_snapshot():
    """Test that DataIngestion.get_business_snapshot returns a valid BusinessSnapshot with data."""
    ingestion = DataIngestion()
    snapshot = ingestion.get_business_snapshot()
    # Assert type
    assert isinstance(snapshot, BusinessSnapshot)
    # Assert non-empty lists
    assert snapshot.products, "Products list should not be empty"
    assert snapshot.audiences, "Audiences list should not be empty"
    assert snapshot.historical_performance, "Historical performance list should not be empty"
