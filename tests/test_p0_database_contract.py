"""P0 safety tests: no real Neon connection is opened."""
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
source = (ROOT / "db.py").read_text(encoding="utf-8")

def test_dedicated_database_url_required():
    assert "WERO_ELETRICO_DATABASE_URL" in source
    assert "no shared DB fallback" in source

def test_separate_schema_and_tables():
    assert "CREATE SCHEMA IF NOT EXISTS wero1eletrico" in source
    assert "wero1eletrico.offers" in source
    assert "wero1eletrico.events" in source

def test_no_synthetic_financial_conversion():
    assert 'if event_type not in ("visit", "click"):' in source
    assert "Financial conversions require" in source
    ast.parse(source)
