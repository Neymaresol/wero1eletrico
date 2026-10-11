"""Security double-check for staging affiliate offer validation (stdlib unittest)."""
import unittest
from affiliate_partners import AffiliateOffer, validate_offer

class OfferValidationTests(unittest.TestCase):
    def test_approved_domain_still_cannot_publish(self):
        result = validate_offer(AffiliateOffer("amazon", "Carregador elétrico", "https://www.amazon.com.br/s?k=carregador", True, True, True))
        self.assertFalse(result["publish_allowed"])
        self.assertEqual(result["financial_status"], "UNCONFIRMED")

    def test_unapproved_account_remains_blocked(self):
        result = validate_offer(AffiliateOffer("amazon", "Carregador", "https://www.amazon.com.br/"))
        self.assertEqual(result["status"], "BLOCKED_PENDING_APPROVAL")

    def test_reject_untrusted_host(self):
        for url in ("https://amazon.com.br.attacker.example/x", "http://amazon.com.br/x", "https://evil.example/x"):
            with self.subTest(url=url), self.assertRaises(ValueError):
                validate_offer(AffiliateOffer("amazon", "Teste", url))

    def test_reject_unknown_partner(self):
        with self.assertRaises(ValueError):
            validate_offer(AffiliateOffer("unknown", "Teste", "https://example.com/"))

if __name__ == "__main__":
    unittest.main()
