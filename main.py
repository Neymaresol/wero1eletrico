import os
from datetime import datetime, timezone
from fastapi import FastAPI

SERVICE = "wero1eletrico"
VERSION = "0.2.0-dev"
app = FastAPI(title=SERVICE, version=VERSION)

@app.get("/")
def root():
    return {"service": SERVICE, "version": VERSION, "status": "development"}

@app.get("/health")
def health():
    return {"status": "ok", "service": SERVICE, "version": VERSION,
            "mode": os.getenv("WERO_MODE", "development"),
            "time": datetime.now(timezone.utc).isoformat()}
