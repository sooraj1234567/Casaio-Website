from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from accounts.models import SellerPayoutProfile, SellerPayoutRequest

User = get_user_model()


class SellerPayoutRequestTests(TestCase):
    def test_create_payout_request_for_verified_seller_profile(self):
        seller = User.objects.create_user(
            username="seller1",
            email="seller1@example.com",
            password="StrongPass123!",
            role="seller",
        )

        profile = SellerPayoutProfile.objects.create(
            seller=seller,
            account_holder_name="Test Seller",
            bank_name="Test Bank",
            account_number="1234567890",
            ifsc_code="HDFC0001234",
            is_verified=True,
        )

        payout_request = SellerPayoutRequest.objects.create(
            seller=seller,
            payout_profile=profile,
            amount=Decimal("2500.00"),
            status="pending",
        )

        self.assertEqual(payout_request.amount, Decimal("2500.00"))
        self.assertEqual(payout_request.status, "pending")
        self.assertEqual(payout_request.seller, seller)
        self.assertEqual(payout_request.payout_profile, profile)
