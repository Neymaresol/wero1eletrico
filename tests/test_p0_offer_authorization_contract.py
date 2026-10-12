"""P0 safe publication contract: staging fixtures must never be published."""
import unittest
from urllib.parse import urlparse

def publishable(offer, allowed_domains):
    url = urlparse(offer.get("affiliate_url") or "")
    host = (url.hostname or "").lower()
    return (offer.get("approved") is True
            and offer.get("title") != "INTERNAL_STAGING_TEST"
            and bool(offer.get("partner"))
            and url.scheme == "https"
            and any(host == d or host.endswith("." + d) for d in allowed_domains)
            and bool(offer.get("verified_affiliate_at")))

class P0OfferContracts(unittest.TestCase):
    def test_internal_staging_offer_blocked(self):
        self.assertFalse(publishable({"title":"INTERNAL_STAGING_TEST","partner":"amazon","affiliate_url":"https://amazon.com.br/","approved":False}, {"amazon.com.br"}))
    def test_unverified_link_blocked(self):
        self.assertFalse(publishable({"title":"Real","partner":"amazon","affiliate_url":"https://amazon.com.br/","approved":True}, {"amazon.com.br"}))
    def test_host_spoofing_blocked(self):
        self.assertFalse(publishable({"title":"Real","partner":"amazon","affiliate_url":"https://amazon.com.br.evil.test/","approved":True,"verified_affiliate_at":"2026-10-12"}, {"amazon.com.br"}))
    def test_verified_authorized_offer(self):
        self.assertTrue(publishable({"title":"Real","partner":"amazon","affiliate_url":"https://www.amazon.com.br/example","approved":True,"verified_affiliate_at":"2026-10-12"}, {"amazon.com.br"}))

if __name__ == "__main__":
    unittest.main()
