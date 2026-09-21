from django.test import SimpleTestCase

from checkout.geo import validate_delivery_location


class GeoValidationTests(SimpleTestCase):
    def test_validate_delivery_location_accepts_indian_pin_and_state(self):
        result = validate_delivery_location(
            city="Bengaluru",
            state="Karnataka",
            pincode="560001",
        )

        self.assertTrue(result["is_valid"])
        self.assertEqual(result["country"], "India")
        self.assertEqual(result["pincode"], "560001")
