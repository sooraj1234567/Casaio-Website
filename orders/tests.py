from django.test import SimpleTestCase

from orders.shipping import build_shiprocket_payload


class ShiprocketPayloadTests(SimpleTestCase):
    def test_build_shiprocket_payload_includes_order_and_customer_fields(self):
        payload = build_shiprocket_payload(
            order_number="CAS-20260920-000123",
            customer_name="Priya Sharma",
            phone="9876543210",
            address_line="12 Main Road",
            city="Bengaluru",
            state="Karnataka",
            pincode="560001",
            amount="499.00",
            product_name="Wireless Headphones",
        )

        self.assertEqual(payload["order_id"], "CAS-20260920-000123")
        self.assertEqual(payload["shipping_customer_name"], "Priya Sharma")
        self.assertEqual(payload["shipping_pincode"], "560001")
        self.assertEqual(payload["order_items"][0]["name"], "Wireless Headphones")
