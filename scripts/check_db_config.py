"""Read-only isolated database configuration validation; no credentials printed."""
import json
import os
from urllib.parse import urlparse

def inspect(env=None):
    env=os.environ if env is None else env
    raw=env.get("WERO_ELETRICO_DATABASE_URL","")
    if not raw:
        return {"configured":False,"valid_format":False,"isolated":False}
    p=urlparse(raw)
    valid=p.scheme in ("postgres","postgresql") and bool(p.hostname and p.path.strip("/"))
    isolated=raw not in [x for x in (env.get("DATABASE_URL"),env.get("WERO_MERCADOS_DATABASE_URL")) if x]
    return {"configured":True,"valid_format":bool(valid),"isolated":isolated}

if __name__=="__main__":
    print(json.dumps(inspect()))
