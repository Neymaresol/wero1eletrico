import os
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException
from db import connect

SERVICE = "wero1eletrico"
VERSION = "0.2.1-dev"
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
