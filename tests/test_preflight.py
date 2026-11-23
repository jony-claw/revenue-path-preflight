from pathlib import Path
import json
import tempfile
import unittest
import preflight

ROOT = Path(__file__).resolve().parents[1]
CATALOG = json.loads((ROOT / "platforms.json").read_text())

class PreflightTests(unittest.TestCase):
    def test_minimal_portugal_profile_has_distribution_but_no_paid_path(self):
        report = preflight.evaluate({"country": "PT", "capabilities": ["github_account", "tested_product"]}, CATALOG)
        by_name = {x["platform"]: x for x in report["results"]}
        self.assertEqual(by_name["GitHub public release"]["status"], "distribution_only")
        self.assertEqual(by_name["Apify Store"]["status"], "blocked")
        self.assertEqual(by_name["Ko-fi Shop"]["status"], "blocked")
        self.assertEqual(by_name["Lemon Squeezy"]["status"], "unavailable")
        self.assertEqual(by_name["Lemon Squeezy"]["blockers"], ["service_retired"])

    def test_complete_apify_profile_is_ready(self):
        capabilities = ["apify_account", "accept_store_terms", "tested_product", "government_id", "billing_details", "payout_method"]
        report = preflight.evaluate({"country": "PT", "capabilities": capabilities}, CATALOG)
        row = next(x for x in report["results"] if x["platform"] == "Apify Store")
        self.assertEqual(row["status"], "payment_path_ready")

    def test_listing_only_is_distinct_from_payout_ready(self):
        capabilities = ["gumroad_account", "tested_product"]
        report = preflight.evaluate({"country": "PT", "capabilities": capabilities}, CATALOG)
        row = next(x for x in report["results"] if x["platform"] == "Gumroad")
        self.assertEqual(row["status"], "listing_only")
        self.assertIn("payout_missing:government_id", row["blockers"])

    def test_stripe_direct_merchant_requires_compliance_owner(self):
        capabilities = ["stripe_account", "tested_product", "government_id", "bank_account"]
        report = preflight.evaluate({"country": "PT", "capabilities": capabilities}, CATALOG)
        row = next(x for x in report["results"] if x["platform"] == "Stripe Billing + Tax")
        self.assertEqual(row["status"], "listing_only")
        self.assertIn("payout_missing:tax_registrations", row["blockers"])
        self.assertIn("payout_missing:compliance_owner", row["blockers"])

if __name__ == "__main__":
    unittest.main()
