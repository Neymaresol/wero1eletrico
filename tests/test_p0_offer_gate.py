import unittest
from p0_offer_gate import approved_public_offer, publication_readiness

class OfferGateTests(unittest.TestCase):
    def setUp(self):
        self.offer = dict(offer_id="staging-gap03-durability-20261010", partner="amazon",
                          title="INTERNAL_STAGING_TEST", affiliate_url="https://amazon.com.br/", approved=False)
    def test_staging_sentinel_is_never_public(self):
        self.assertFalse(approved_public_offer(self.offer))
        self.assertEqual(publication_readiness([self.offer])["eligible_count"], 0)
    def test_unapproved_is_blocked(self):
        self.assertFalse(approved_public_offer(dict(offer_id="a", partner="amazon", title="A",
                            affiliate_url="https://amzn.to/example", approved=False)))
    def test_generic_amazon_url_is_not_affiliate_link(self):
        self.assertFalse(approved_public_offer(dict(offer_id="a", partner="amazon", title="A",
                            affiliate_url="https://amazon.com.br/", approved=True)))
    def test_no_publication_or_financial_invention(self):
        result = publication_readiness([])
        self.assertFalse(result["publication_enabled"])
        self.assertFalse(result["partner_authorization_verified"])
if __name__ == "__main__":
    unittest.main()
