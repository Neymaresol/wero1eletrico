"""Decision-support rules for the future AI commercial layer.

No autonomous publication, financial confirmation, or external API calls.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class OfferMetrics:
    offer_id: str
    visits: int
    clicks: int
    confirmed_conversions: int
    partner_authorized: bool

def recommend(metrics: OfferMetrics) -> dict:
    if any(x < 0 for x in (metrics.visits, metrics.clicks, metrics.confirmed_conversions)):
        raise ValueError("Metrics cannot be negative")
    if metrics.clicks > metrics.visits or metrics.confirmed_conversions > metrics.clicks:
        raise ValueError("Inconsistent funnel metrics")
    if not metrics.partner_authorized:
        action = "BLOCK_UNAUTHORIZED_PARTNER"
    elif metrics.visits == 0:
        action = "ACQUIRE_QUALIFIED_TRAFFIC"
    elif metrics.clicks == 0:
        action = "IMPROVE_OFFER_PRESENTATION"
    elif metrics.confirmed_conversions == 0:
        action = "REVIEW_LANDING_AND_PARTNER_CONVERSION"
    else:
        action = "REVIEW_SCALING_WITH_HUMAN_APPROVAL"
    return {"offer_id": metrics.offer_id, "action": action,
            "click_through_rate": round(metrics.clicks / metrics.visits, 4) if metrics.visits else 0,
            "conversion_rate": round(metrics.confirmed_conversions / metrics.clicks, 4) if metrics.clicks else 0,
            "confirmed_conversions": metrics.confirmed_conversions,
            "requires_human_approval": True}
