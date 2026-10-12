"""Pure validation gate: no DB writes, publishing or affiliate redirects."""
from urllib.parse import urlsplit

def approved_public_offer(offer):
    if not isinstance(offer, dict) or offer.get("approved") is not True:
        return False
    ident = str(offer.get("offer_id") or "").strip()
    title = str(offer.get("title") or "").strip()
    partner = str(offer.get("partner") or "").strip()
    url = str(offer.get("affiliate_url") or "").strip()
    if not ident or ident.startswith("staging-") or not title or title == "INTERNAL_STAGING_TEST" or not partner:
        return False
    try:
        parsed = urlsplit(url)
        host = (parsed.hostname or "").lower()
    except ValueError:
        return False
    if parsed.scheme != "https" or not host or parsed.username or parsed.password:
        return False
    if host in {"amazon.com.br", "www.amazon.com.br"} and parsed.path in {"", "/"} and not parsed.query:
        return False
    return True

def publication_readiness(offers):
    eligible = [offer["offer_id"] for offer in offers if approved_public_offer(offer)]
    return {"eligible_ids": eligible, "eligible_count": len(eligible),
            "publication_enabled": False,
            "partner_authorization_verified": False,
            "note": "Passing format validation does not verify partner authorization or enable publication."}
