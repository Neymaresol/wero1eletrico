"""Isolated PostgreSQL storage for Wero1Eletrico; never falls back to another bot."""
import os
from urllib.parse import urlparse
import psycopg

SERVICE = "wero1eletrico"

def database_url():
    url = os.getenv("WERO_ELETRICO_DATABASE_URL", "").strip()
    if not url:
        raise RuntimeError("WERO_ELETRICO_DATABASE_URL is required; no shared DB fallback")
    parsed = urlparse(url)
    if parsed.scheme not in ("postgresql", "postgres") or not parsed.hostname or not parsed.path.strip("/"):
        raise ValueError("Invalid PostgreSQL URL")
    if os.getenv("WERO_MERCADOS_DATABASE_URL") == url or os.getenv("DATABASE_URL") == url:
        raise RuntimeError("Refusing a database URL matching a shared/other service connection")
    return url

def connect():
    return psycopg.connect(database_url(), connect_timeout=5, application_name=SERVICE)

def initialize():
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("CREATE SCHEMA IF NOT EXISTS wero1eletrico")
            cur.execute("""CREATE TABLE IF NOT EXISTS wero1eletrico.offers (
                offer_id TEXT PRIMARY KEY,
                partner TEXT NOT NULL,
                title TEXT NOT NULL,
                affiliate_url TEXT NOT NULL,
                approved BOOLEAN NOT NULL DEFAULT FALSE,
                created_at TIMESTAMPTZ NOT NULL DEFAULT now()
            )""")
            cur.execute("""CREATE TABLE IF NOT EXISTS wero1eletrico.events (
                event_id TEXT PRIMARY KEY,
                offer_id TEXT NOT NULL REFERENCES wero1eletrico.offers(offer_id),
                event_type TEXT NOT NULL CHECK (event_type IN ('visit','click','partner_confirmed_sale')),
                partner_reference TEXT,
                created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                CHECK (event_type <> 'partner_confirmed_sale' OR partner_reference IS NOT NULL)
            )""")

def save_offer(offer_id, partner, title, affiliate_url, approved=False):
    from affiliate_partners import AffiliateOffer, validate_offer
    validate_offer(AffiliateOffer(partner, title, affiliate_url))
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("""INSERT INTO wero1eletrico.offers
                (offer_id, partner, title, affiliate_url, approved)
                VALUES (%s,%s,%s,%s,%s)
                ON CONFLICT (offer_id) DO UPDATE SET
                partner=EXCLUDED.partner, title=EXCLUDED.title,
                affiliate_url=EXCLUDED.affiliate_url, approved=EXCLUDED.approved""",
                (offer_id, partner, title, affiliate_url, approved))

def record_event(event_id, offer_id, event_type, partner_reference=None):
    if event_type not in ("visit", "click"):
        raise ValueError("Financial conversions require a separately authenticated partner integration")
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("""INSERT INTO wero1eletrico.events
                (event_id, offer_id, event_type) VALUES (%s,%s,%s)
                ON CONFLICT (event_id) DO NOTHING""",
                (event_id, offer_id, event_type))
