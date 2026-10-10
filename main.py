import os
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException
from db import connect

SERVICE = "wero1eletrico"
VERSION = "0.2.2-dev"
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
