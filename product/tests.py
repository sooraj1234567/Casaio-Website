from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import Client, SimpleTestCase, TestCase
from django.urls import reverse

from product.sync import build_supplier_product_payload


class ProductSyncTests(SimpleTestCase):
    def test_build_supplier_product_payload_maps_supplier_fields(self):
        payload = build_supplier_product_payload(
            name="USB Type-C Cable",
            description="Fast charging cable",
            supplier_price="120.00",
            selling_price="299.00",
            stock=25,
            category_name="Electronics",
        )

        self.assertEqual(payload["name"], "USB Type-C Cable")
        self.assertEqual(payload["supplier_price"], Decimal("120.00"))
        self.assertEqual(payload["selling_price"], Decimal("299.00"))
        self.assertEqual(payload["stock"], 25)
        self.assertEqual(payload["category_name"], "Electronics")


class ProductCsvImportViewTests(TestCase):
    def test_seller_csv_import_page_is_available(self):
        user = get_user_model().objects.create_user(
            username="seller",
            email="seller@example.com",
            password="StrongPass123!",
            role="seller",
        )

        client = Client()
        client.force_login(user)

        response = client.get(reverse("seller_csv_import"))

        self.assertEqual(response.status_code, 200)
