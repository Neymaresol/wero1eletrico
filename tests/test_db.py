import pytest
import db

def test_missing_url_fails_closed(monkeypatch):
    monkeypatch.delenv("WERO_ELETRICO_DATABASE_URL", raising=False)
    with pytest.raises(RuntimeError, match="required"):
        db.database_url()

def test_rejects_shared_database(monkeypatch):
    url = "postgresql://user:password@localhost:5432/mercados"
    monkeypatch.setenv("WERO_ELETRICO_DATABASE_URL", url)
    monkeypatch.setenv("DATABASE_URL", url)
    with pytest.raises(RuntimeError, match="Refusing"):
        db.database_url()

def test_valid_isolated_url(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("WERO_MERCADOS_DATABASE_URL", raising=False)
    url = "postgresql://user:password@localhost:5432/wero1eletrico"
    monkeypatch.setenv("WERO_ELETRICO_DATABASE_URL", url)
    assert db.database_url() == url

def test_conversion_not_inserted_without_partner_verification(monkeypatch):
    monkeypatch.setattr(db, "connect", lambda: pytest.fail("DB must not be called"))
    with pytest.raises(ValueError, match="authenticated partner"):
        db.record_event("e1", "o1", "partner_confirmed_sale", "fake")

def test_invalid_url(monkeypatch):
    monkeypatch.setenv("WERO_ELETRICO_DATABASE_URL", "sqlite:///tmp/file.db")
    with pytest.raises(ValueError):
        db.database_url()
