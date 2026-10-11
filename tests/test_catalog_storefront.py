"""Offline regression contracts for staging storefront."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def test_staging_catalog_never_redirects_unapproved_offers():
    src=(ROOT/"main.py").read_text(encoding="utf-8")
    section=src.split('@app.get("/catalogo"',1)[1].split('@app.get("/api/acquisition")',1)[0]
    assert 'WERO_MODE' in section and 'staging' in section
    assert "affiliate_url" not in section
    assert "RedirectResponse" not in section
    assert "escape(str(title))" in section
def test_categories_are_not_fake_offers():
    src=(ROOT/"catalog_categories.py").read_text(encoding="utf-8")
    assert "CATEGORIES" in src
    assert "affiliate_url" not in src
