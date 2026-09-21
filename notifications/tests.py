from unittest.mock import patch

from django.test import SimpleTestCase

from notifications.services import (
    build_email_payload,
    build_sms_payload,
    build_whatsapp_payload,
    get_sms_provider,
    send_whatsapp_notification,
)
from notifications.views import parse_whatsapp_status_payload, verify_whatsapp_webhook_signature


class NotificationPayloadTests(SimpleTestCase):
    def test_build_email_payload_includes_subject_and_recipient(self):
        payload = build_email_payload(
            subject="Order confirmed",
            recipient="customer@example.com",
            message="Your order is confirmed.",
        )

        self.assertEqual(payload["subject"], "Order confirmed")
        self.assertIn("customer@example.com", payload["to"])
        self.assertIn("Your order is confirmed.", payload["body"])

    def test_build_sms_payload_includes_phone_and_message(self):
        payload = build_sms_payload(
            phone_number="+919876543210",
            message="Your order has shipped.",
        )

        self.assertEqual(payload["to"], "+919876543210")
        self.assertEqual(payload["body"], "Your order has shipped.")

    def test_get_sms_provider_defaults_to_twilio(self):
        self.assertEqual(get_sms_provider(), "twilio")

    def test_build_whatsapp_payload_includes_template_and_number(self):
        payload = build_whatsapp_payload(
            phone_number="+919876543210",
            template_name="order_confirmed",
            parameters=["#12345", "Rs. 1499"],
        )

        self.assertEqual(payload["to"], "+919876543210")
        self.assertEqual(payload["template_name"], "order_confirmed")
        self.assertEqual(payload["parameters"], ["#12345", "Rs. 1499"])

    @patch("notifications.services.requests.post")
    def test_send_whatsapp_notification_calls_meta_graph_api(self, mock_post):
        mock_post.return_value.status_code = 200

        with patch.dict(
            "os.environ",
            {
                "WHATSAPP_ACCESS_TOKEN": "token-123",
                "WHATSAPP_PHONE_NUMBER_ID": "123456789",
            },
            clear=False,
        ):
            result = send_whatsapp_notification(
                phone_number="+919876543210",
                template_name="order_confirmed",
                parameters=["#12345", "Rs. 1499"],
            )

        self.assertTrue(result)
        self.assertEqual(mock_post.call_count, 1)
        self.assertIn("graph.facebook.com", mock_post.call_args[0][0])

    def test_parse_whatsapp_status_payload_extracts_delivery_status(self):
        payload = {
            "entry": [{
                "changes": [{
                    "value": {
                        "statuses": [{
                            "id": "wamid.123",
                            "status": "sent",
                            "recipient_id": "919876543210",
                            "timestamp": "1712345678",
                        }]
                    }
                }]
            }]
        }

        status_info = parse_whatsapp_status_payload(payload)
        self.assertEqual(status_info["message_id"], "wamid.123")
        self.assertEqual(status_info["status"], "sent")
        self.assertEqual(status_info["recipient_id"], "919876543210")

    def test_verify_whatsapp_webhook_signature_accepts_matching_secret(self):
        import hashlib
        import hmac

        secret = "whatsapp-secret"
        body = b'{"sample": true}'
        signature = "sha256=" + hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()

        with patch.dict("os.environ", {"WHATSAPP_WEBHOOK_SECRET": secret}, clear=False):
            self.assertTrue(verify_whatsapp_webhook_signature(body, signature))
