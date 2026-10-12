"""Offline commercial safety contracts; no database, network or partner calls."""
from pathlib import Path
import ast

ROOT = Path(__file__).resolve().parents[1]

def test_commercial_router_parses_and_is_packaged():
    source = (ROOT / "commercial_storefront.py").read_text(encoding="utf-8")
    ast.parse(source)
    docker = (ROOT / "Dockerfile").read_text(encoding="utf-8")
    main = (ROOT / "main.py").read_text(encoding="utf-8")
    copy_lines = [line.split() for line in docker.splitlines() if line.startswith("COPY ")]
    assert any("commercial_storefront.py" in parts[1:-1] and "p0_offer_gate.py" in parts[1:-1] and parts[-1] == "./" for parts in copy_lines)
    assert "app.include_router(commercial_router)" in main

def test_approval_requires_auth_and_evidence():
    src = (ROOT / "commercial_storefront.py").read_text(encoding="utf-8")
    assert 'authorize(x_diagnostic_token)' in src
    assert 'evidence.account_approved' in src
    assert 'evidence.link_verified' in src
    assert 'evidence.channel_approved' in src
    assert 'approved=TRUE' in src

def test_redirect_requires_approved_offer_and_validated_partner():
    src = (ROOT / "commercial_storefront.py").read_text(encoding="utf-8")
    section = src.split('@router.get("/go/{offer_id}")', 1)[1].split('@router.get("/vitrine"', 1)[0]
    assert 'approved=TRUE' in section
    assert 'approved_url(*row)' in section
    assert 'record' not in section or "'click'" in section
    assert "'click'" in section
    assert "RedirectResponse" in section
    assert "partner_confirmed_sale" not in section

def test_staging_gate_on_all_public_routes():
    src = (ROOT / "commercial_storefront.py").read_text(encoding="utf-8")
    for route in ('@router.get("/api/storefront/offers")', '@router.get("/go/{offer_id}")', '@router.get("/vitrine"'):
        section = src.split(route,1)[1].split('def ',2)[1]
        assert "staging_only()" in section

def test_no_price_or_commission_fabrication():
    src = (ROOT / "commercial_storefront.py").read_text(encoding="utf-8")
    assert 'commission_brl' not in src
    assert 'confirmed_sales' not in src
