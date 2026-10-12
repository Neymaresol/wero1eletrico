"""Staging-only affiliate storefront. No synthetic sales or unapproved redirects."""
import os
import secrets
import uuid
from html import escape
from urllib.parse import urlparse
from fastapi import APIRouter, Header, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel
from db import connect
from affiliate_partners import AffiliateOffer, validate_offer
from p0_offer_gate import approved_public_offer

router = APIRouter()

def staging_only():
    if os.getenv("WERO_MODE") != "staging":
        raise HTTPException(404, "not_found")

def approved_url(partner, title, url):
    try:
        validate_offer(AffiliateOffer(partner=partner, title=title, affiliate_url=url))
    except (ValueError, TypeError):
        raise HTTPException(409, "invalid_partner_url")
    if not approved_public_offer({"offer_id": "manual-check", "partner": partner, "title": title, "affiliate_url": url, "approved": True}):
        raise HTTPException(409, "invalid_partner_url")
    parsed = urlparse(url)
    if parsed.fragment or any(c in url for c in "\r\n"):
        raise HTTPException(409, "invalid_partner_url")
    return url

def authorize(token):
    expected = os.getenv("WERO_ELETRICO_DIAGNOSTIC_TOKEN", "")
    if not expected:
        raise HTTPException(503, "staging_write_not_configured")
    if not token or not secrets.compare_digest(token, expected):
        raise HTTPException(403, "forbidden")

class ApprovalEvidence(BaseModel):
    account_approved: bool
    link_verified: bool
    channel_approved: bool

@router.post("/internal/commercial/offers/{offer_id}/approve")
def approve(offer_id: str, evidence: ApprovalEvidence, x_diagnostic_token: str | None = Header(default=None)):
    """Manual evidence attestation by authorized operator; never self-approves."""
    staging_only()
    authorize(x_diagnostic_token)
    if not all((evidence.account_approved, evidence.link_verified, evidence.channel_approved)):
        raise HTTPException(422, "approval_evidence_incomplete")
    with connect() as conn:
        with conn.cursor() as cur:
            if conn.info.dbname != "wero1eletrico":
                raise HTTPException(503, "wrong_database")
            cur.execute("SELECT partner,title,affiliate_url FROM wero1eletrico.offers WHERE offer_id=%s AND offer_id NOT LIKE 'staging-%%' FOR UPDATE", (offer_id,))
            row = cur.fetchone()
            if row is None:
                raise HTTPException(404, "offer_not_found")
            approved_url(*row)
            if not approved_public_offer({"offer_id": offer_id, "partner": row[0], "title": row[1], "affiliate_url": row[2], "approved": True}):
                raise HTTPException(409, "invalid_offer")
            cur.execute("UPDATE wero1eletrico.offers SET approved=TRUE WHERE offer_id=%s", (offer_id,))
    return {"offer_id": offer_id, "approved": True, "evidence_attested": True, "sales_created": False}

@router.get("/api/storefront/offers")
def published_offers():
    staging_only()
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("""SELECT offer_id,partner,title,affiliate_url FROM wero1eletrico.offers
                WHERE approved=TRUE AND offer_id NOT LIKE 'staging-%%'
                ORDER BY created_at DESC LIMIT 200""")
            rows = cur.fetchall()
    return {"service": "wero1eletrico", "mode": "staging", "offers": [
        {"id": oid, "partner": partner, "title": title, "buy_path": "/go/" + oid}
        for oid,partner,title,url in rows if approved_public_offer({"offer_id": oid, "partner": partner, "title": title, "affiliate_url": url, "approved": True}) and _valid(partner,title,url)], "affiliate_urls_exposed": False}

@router.get("/go/{offer_id}")
def go_to_partner(offer_id: str):
    staging_only()
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("""SELECT partner,title,affiliate_url FROM wero1eletrico.offers
                WHERE offer_id=%s AND approved=TRUE AND offer_id NOT LIKE 'staging-%%'""", (offer_id,))
            row = cur.fetchone()
            if row is None:
                raise HTTPException(404, "offer_not_approved")
            if not approved_public_offer({"offer_id": offer_id, "partner": row[0], "title": row[1], "affiliate_url": row[2], "approved": True}):
                raise HTTPException(404, "offer_not_approved")
            target = approved_url(*row)
            cur.execute("INSERT INTO wero1eletrico.events(event_id,offer_id,event_type) VALUES (%s,%s,'click')", (str(uuid.uuid4()),offer_id))
    return RedirectResponse(target, status_code=302, headers={"Referrer-Policy": "no-referrer", "Cache-Control": "no-store"})

@router.get("/vitrine", response_class=HTMLResponse)
def storefront():
    staging_only()
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("""SELECT offer_id,partner,title,affiliate_url FROM wero1eletrico.offers
                WHERE approved=TRUE AND offer_id NOT LIKE 'staging-%%'
                ORDER BY created_at DESC LIMIT 200""")
            rows = cur.fetchall()
            approved = [(oid, partner, title) for oid,partner,title,url in rows if approved_public_offer({"offer_id": oid, "partner": partner, "title": title, "affiliate_url": url, "approved": True}) and _valid(partner,title,url)]
            for oid,_,_ in approved:
                cur.execute("INSERT INTO wero1eletrico.events(event_id,offer_id,event_type) VALUES (%s,%s,'visit')", (str(uuid.uuid4()),oid))
    cards = "".join("<article><small>" + escape(partner) + "</small><h2>" + escape(title) +
                    "</h2><a href='/go/" + escape(oid, quote=True) +
                    "' rel='nofollow sponsored noopener'>Ver oferta no parceiro</a></article>"
                    for oid,partner,title in approved)
    if not cards:
        cards = "<p>Nenhuma oferta aprovada e validada para publicação.</p>"
    return """<!doctype html><html lang="pt-BR"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Wero1Elétrico | Vitrine staging</title>
<style>body{font-family:system-ui;margin:0;background:#f5f7fa;color:#14253b}
header{background:#102a43;color:white;padding:28px}main{max-width:1000px;margin:auto;padding:24px}
section{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:16px}
article{background:white;border-radius:12px;padding:22px;border:1px solid #ddd}
a{display:inline-block;background:#1466a3;color:white;padding:12px;border-radius:8px}
</style><header><h1>Wero1Elétrico</h1><p>Vitrine comercial — staging</p></header>
<main><h2>Ofertas aprovadas</h2><section>""" + cards + """</section>
<p>Links de parceiros. Preços e disponibilidade devem ser confirmados na loja.</p></main></html>"""

def _valid(partner,title,url):
    try:
        approved_url(partner,title,url)
        return True
    except HTTPException:
        return False
