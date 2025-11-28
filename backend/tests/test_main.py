import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def get_example_snapshot():
    return {
        "products": [{"id": "p1", "name": "Product1", "price": 10.0}],
        "audiences": [{"segment": "gamers"}],
        "historical_performance": [{
            "channel": "facebook",
            "impressions": 1000,
            "clicks": 50,
            "conversions": 5,
            "spend": 100.0,
            "revenue": 500.0
        }]
    }

def test_root():
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json() == {"message": "Welcome to the Agentic Ad Optimizer API"}

def test_create_experiment_plan():
    snapshot = get_example_snapshot()
    resp = client.post("/experiment-plan", json=snapshot)
    assert resp.status_code == 200
    data = resp.json()
    assert data["experiment_id"] == "exp_001"
    assert len(data["variants"]) == 3

def test_generate_creative_variants():
    snapshot = get_example_snapshot()
    plan_resp = client.post("/experiment-plan", json=snapshot)
    plan = plan_resp.json()
    resp = client.post("/creative-variants", json=plan)
    assert resp.status_code == 200
    creatives = resp.json()
    assert len(creatives) == len(plan["variants"])
    for creative in creatives:
        assert "headline" in creative

def test_evaluate_creatives():
    snapshot = get_example_snapshot()
    plan = client.post("/experiment-plan", json=snapshot).json()
    creatives = client.post("/creative-variants", json=plan).json()
    resp = client.post("/score-creatives", json=creatives)
    assert resp.status_code == 200
    scores = resp.json()
    assert len(scores) == len(creatives)
    for score in scores:
        assert "overall_strength" in score

def test_process_experiment_results():
    snapshot = get_example_snapshot()
    plan = client.post("/experiment-plan", json=snapshot).json()
    results = {
        "experiment_id": plan["experiment_id"],
        "results": [
            {
                "variant_id": "A",
                "impressions": 1000,
                "clicks": 50,
                "spend": 200.0,
                "conversions": 10,
                "revenue": 2000.0,
                "profit": 1800.0,
                "cac": 20.0,
                "roas": 10.0
            },
            {
                "variant_id": "B",
                "impressions": 800,
                "clicks": 40,
                "spend": 200.0,
                "conversions": 8,
                "revenue": 1500.0,
                "profit": 1300.0,
                "cac": 25.0,
                "roas": 7.5
            }
        ],
        "winner_variant_id": "A"
    }
    resp = client.post("/results", json=results)
    assert resp.status_code == 200
    rec = resp.json()
    assert rec["experiment_id"] == plan["experiment_id"]
    assert len(rec["recommended_variants"]) == 2
    assert "summary" in rec
