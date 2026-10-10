"""Amazon Associates tracking isolation for Wero1Eletrico.

No Amazon credentials are stored here. This module does not confirm sales.
"""
import os
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

SERVICE = "wero1eletrico"
TRACKING_ID = os.getenv("WERO_ELETRICO_AMAZON_TRACKING_ID", "").strip()
APPROVED = os.getenv("WERO_ELETRICO_AMAZON_ID_APPROVED", "false").lower() == "true"
ALLOWED_HOSTS = {"amazon.com.br", "www.amazon.com.br"}


def affiliate_link(url: str) -> str:
    """Return an approved Amazon Brazil affiliate URL, fail closed otherwise."""
    if not APPROVED or not TRACKING_ID:
        raise ValueError("Amazon tracking ID not yet approved/configured")
    if not TRACKING_ID.endswith("-20") or TRACKING_ID == "wero1mercados-20":
        raise ValueError("Invalid or shared tracking ID")
    parsed = urlsplit(url)
    if parsed.scheme != "https" or (parsed.hostname or "").lower() not in ALLOWED_HOSTS:
        raise ValueError("Only HTTPS amazon.com.br links are permitted")
    if parsed.username or parsed.password or parsed.port:
        raise ValueError("Unexpected URL authority")
    params = [(k, v) for k, v in parse_qsl(parsed.query, keep_blank_values=True) if k.lower() != "tag"]
    params.append(("tag", TRACKING_ID))
    return urlunsplit((parsed.scheme, parsed.netloc, parsed.path, urlencode(params), parsed.fragment))


def attribution_metadata(campaign: str) -> dict:
    return {"robot": SERVICE, "channel": "amazon_associates", "campaign": campaign,
            "tracking_id": TRACKING_ID if APPROVED else None,
            "sales_confirmed": 0, "commission_confirmed_brl": "0.00",
            "financial_source": "amazon_report_required"}
