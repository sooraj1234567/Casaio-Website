from django.test import SimpleTestCase

from analytics.services import (
    build_ads_campaign_summary,
    build_ga4_event,
    build_google_ads_conversion,
    build_meta_ads_event,
    build_meta_pixel_event,
    get_analytics_provider,
    get_google_ads_client,
    get_meta_ads_client,
)


class AnalyticsIntegrationTests(SimpleTestCase):
    def test_get_analytics_provider_defaults_to_ga4(self):
        self.assertEqual(get_analytics_provider(), "ga4")

    def test_build_ga4_event_contains_event_name_and_params(self):
        payload = build_ga4_event(
            event_name="purchase",
            params={"currency": "INR", "value": 1999.0},
            user_id="user-101",
        )

        self.assertEqual(payload["name"], "purchase")
        self.assertEqual(payload["params"]["currency"], "INR")
        self.assertEqual(payload["user_id"], "user-101")

    def test_build_meta_pixel_event_contains_standard_fields(self):
        payload = build_meta_pixel_event(
            event_name="Lead",
            value=2499.0,
            currency="INR",
            content_ids=["sku-1"],
        )

        self.assertEqual(payload["event_name"], "Lead")
        self.assertEqual(payload["currency"], "INR")
        self.assertEqual(payload["content_ids"], ["sku-1"])

    def test_build_ads_campaign_summary_has_key_metrics(self):
        summary = build_ads_campaign_summary(
            campaign_name="Summer Sale",
            spend=2500.00,
            clicks=1240,
            conversions=86,
            revenue=158400.00,
        )

        self.assertEqual(summary["campaign_name"], "Summer Sale")
        self.assertEqual(summary["spend"], 2500.00)
        self.assertEqual(summary["conversions"], 86)
        self.assertGreater(summary["roas"], 0)

    def test_get_google_ads_client_returns_stub_details(self):
        client = get_google_ads_client()

        self.assertEqual(client["provider"], "google_ads")
        self.assertTrue(client["stub"])
        self.assertIn("customer_id", client)

    def test_build_google_ads_conversion_contains_sale_fields(self):
        payload = build_google_ads_conversion(
            conversion_name="purchase",
            value=1999.0,
            currency="INR",
            order_id="ORDER-101",
        )

        self.assertEqual(payload["conversion_name"], "purchase")
        self.assertEqual(payload["value"], 1999.0)
        self.assertEqual(payload["currency"], "INR")
        self.assertEqual(payload["order_id"], "ORDER-101")

    def test_get_meta_ads_client_returns_stub_details(self):
        client = get_meta_ads_client()

        self.assertEqual(client["provider"], "meta_ads")
        self.assertTrue(client["stub"])
        self.assertIn("pixel_id", client)

    def test_build_meta_ads_event_contains_standard_ad_fields(self):
        payload = build_meta_ads_event(
            event_name="Purchase",
            value=1999.0,
            currency="INR",
            content_ids=["sku-1"],
        )

        self.assertEqual(payload["event_name"], "Purchase")
        self.assertEqual(payload["value"], 1999.0)
        self.assertEqual(payload["currency"], "INR")
        self.assertEqual(payload["content_ids"], ["sku-1"])
