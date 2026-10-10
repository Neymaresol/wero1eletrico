import pytest
from affiliate_partners import AffiliateOffer, validate_offer

@pytest.mark.parametrize("partner,url", [
    ("amazon", "https://www.amazon.com.br/dp/EXAMPLE"),
    ("mercadolivre", "https://produto.mercadolivre.com.br/item"),
    ("shopee", "https://shopee.com.br/product"),
])
def test_supported_partners_block_until_approved(partner, url):
    assert validate_offer(AffiliateOffer(partner, "test", url))["status"] == "BLOCKED_PENDING_APPROVAL"

def test_prevent_domain_spoofing():
    with pytest.raises(ValueError):
        validate_offer(AffiliateOffer("amazon", "test", "https://amazon.com.br.evil.test/item"))

def test_approved_requires_manual_review():
    o = AffiliateOffer("amazon", "test", "https://amzn.to/example", True, True, True)
    result = validate_offer(o)
    assert result["status"] == "READY_FOR_MANUAL_REVIEW"
    assert result["publish_allowed"] is False
