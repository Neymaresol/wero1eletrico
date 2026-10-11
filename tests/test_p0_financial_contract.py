"""Staging must never present simulated sales or enable campaigns."""
from pathlib import Path
s=(Path(__file__).resolve().parents[1]/"main.py").read_text()
def test_staging_commercial_gate():
    assert '"campaign_execution_enabled": False' in s
    assert '"publication_verified": False' in s
    assert "WHERE offer_id NOT LIKE 'staging-%'" in s
