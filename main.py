import os
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException, Header
from db import connect
import secrets
import uuid

SERVICE = "wero1eletrico"
VERSION = "0.2.4-dev"
app = FastAPI(title=SERVICE, version=VERSION)

@app.get("/")
def root():
    return {"service": SERVICE, "version": VERSION, "status": "development"}

@app.get("/health")
def health():
    return {"status": "ok", "service": SERVICE, "version": VERSION,
            "mode": os.getenv("WERO_MODE", "development"),
            "time": datetime.now(timezone.utc).isoformat()}

@app.get("/health/db")
def database_health():
    """Read-only staging DB probe; never reports financial transactions."""
    try:
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT current_database(), to_regclass('wero1eletrico.offers'), to_regclass('wero1eletrico.events')")
                db_name, offers, events = cur.fetchone()
        if db_name != "wero1eletrico" or offers is None or events is None:
            raise HTTPException(status_code=503, detail="database_schema_unavailable")
        return {"status": "ok", "service": SERVICE, "database": "connected", "schema": "ready"}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=503, detail="database_unavailable")

@app.get("/health/db/persistence")
def persistence_health():
    """Staging-only transactional write/read verification; rolls back test row."""
    if os.getenv("WERO_MODE") != "staging":
        raise HTTPException(status_code=404, detail="not_found")
    try:
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT current_database()")
                if cur.fetchone()[0] != "wero1eletrico":
                    raise RuntimeError("wrong_database")
                cur.execute("CREATE TEMP TABLE wero_probe (value TEXT NOT NULL) ON COMMIT DROP")
                cur.execute("INSERT INTO wero_probe(value) VALUES (%s)", ("wero1eletrico-staging-probe",))
                cur.execute("SELECT value FROM wero_probe")
                verified = cur.fetchone()[0] == "wero1eletrico-staging-probe"
            conn.rollback()
        if not verified:
            raise RuntimeError("readback_mismatch")
        return {"status": "ok", "service": SERVICE, "database": "connected",
                "write": "ok", "readback": "ok", "transaction": "rolled_back",
                "scope": "temporary_staging_table"}
    except Exception:
        raise HTTPException(status_code=503, detail="persistence_check_failed")

@app.post("/internal/db/durability-check")
def durability_check(x_diagnostic_token: str | None = Header(default=None)):
    """Authenticated staging-only committed write/read across two DB sessions."""
    expected = os.getenv("WERO_ELETRICO_DIAGNOSTIC_TOKEN", "")
    if os.getenv("WERO_MODE") != "staging" or not expected:
        raise HTTPException(status_code=404, detail="not_found")
    if not x_diagnostic_token or not secrets.compare_digest(x_diagnostic_token, expected):
        raise HTTPException(status_code=403, detail="forbidden")
    probe_id = "staging-probe-" + str(uuid.uuid4())
    try:
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT current_database()")
                if cur.fetchone()[0] != "wero1eletrico":
                    raise RuntimeError("wrong_database")
                cur.execute("""INSERT INTO wero1eletrico.offers
                    (offer_id, partner, title, affiliate_url, approved)
                    VALUES (%s, %s, %s, %s, FALSE)""",
                    (probe_id, "amazon", "INTERNAL_STAGING_TEST", "https://amazon.com.br/"))
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT title, approved FROM wero1eletrico.offers WHERE offer_id=%s", (probe_id,))
                row = cur.fetchone()
        if row != ("INTERNAL_STAGING_TEST", False):
            raise RuntimeError("durability_readback_failed")
        return {"status": "ok", "database": "connected", "committed_write": "ok",
                "new_connection_readback": "ok", "financial_events": "not_created"}
    except Exception:
        raise HTTPException(status_code=503, detail="durability_check_failed")
    finally:
        try:
            with connect() as conn:
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM wero1eletrico.offers WHERE offer_id=%s", (probe_id,))
        except Exception:
            pass

@app.get("/health/db/durable-read")
def durable_read_health():
    """Read the noncommercial Neon sentinel through the staging API."""
    if os.getenv("WERO_MODE") != "staging":
        raise HTTPException(status_code=404, detail="not_found")
    try:
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute("""SELECT title, approved FROM wero1eletrico.offers
                    WHERE offer_id = %s""", ("staging-gap03-durability-20261010",))
                row = cur.fetchone()
        if row != ("INTERNAL_STAGING_TEST", False):
            raise RuntimeError("sentinel_missing")
        return {"status": "ok", "service": SERVICE,
                "durable_record": "verified", "approved": False,
                "sales": "not_created"}
    except Exception:
        raise HTTPException(status_code=503, detail="durable_read_failed")
