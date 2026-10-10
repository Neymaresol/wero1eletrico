import pytest
from ai_strategy import OfferMetrics, recommend

def test_block_unauthorized_partner():
    assert recommend(OfferMetrics("ev1", 10, 2, 0, False))["action"] == "BLOCK_UNAUTHORIZED_PARTNER"

def test_no_traffic():
    assert recommend(OfferMetrics("ev2", 0, 0, 0, True))["action"] == "ACQUIRE_QUALIFIED_TRAFFIC"

def test_conversion_requires_approval():
    result = recommend(OfferMetrics("ev3", 100, 10, 1, True))
    assert result["requires_human_approval"] is True
    assert result["conversion_rate"] == 0.1

def test_invalid_metrics():
    with pytest.raises(ValueError):
        recommend(OfferMetrics("ev4", 1, 2, 0, True))
