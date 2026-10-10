"""Safe affiliate partner registry. No shared credentials or auto-publication."""
from dataclasses import dataclass
from urllib.parse import urlparse

PARTNER_HOSTS = {
    "amazon": ("amazon.com.br", "amzn.to"),
    "mercadolivre": ("mercadolivre.com.br", "mercadolivre.com"),
    "shopee": ("shopee.com.br", "shope.ee"),
}

@dataclass(frozen=True)
class AffiliateOffer:
    partner: str
    title: str
    affiliate_url: str
    account_approved: bool = False
    link_verified: bool = False
    channel_approved: bool = False

def validate_offer(offer: AffiliateOffer) -> dict:
    if offer.partner not in PARTNER_HOSTS:
        raise ValueError("Unknown partner")
    parsed = urlparse(offer.affiliate_url)
    hostname = (parsed.hostname or "").lower()
    allowed = any(hostname == host or hostname.endswith("." + host)
                  for host in PARTNER_HOSTS[offer.partner])
    if parsed.scheme != "https" or not allowed or parsed.username or parsed.password:
        raise ValueError("Affiliate URL must use an approved HTTPS partner domain")
    ready = offer.account_approved and offer.link_verified and offer.channel_approved
    return {"partner": offer.partner, "title": offer.title,
            "status": "READY_FOR_MANUAL_REVIEW" if ready else "BLOCKED_PENDING_APPROVAL",
            "publish_allowed": False,
            "financial_status": "UNCONFIRMED"}
