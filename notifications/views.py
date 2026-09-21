import hashlib
import hmac
import json
import os
from typing import Any, Dict, List

from django.http import HttpResponse, JsonResponse


def verify_whatsapp_webhook_signature(raw_body: bytes, signature: str | None) -> bool:
    """Verify the Meta WhatsApp webhook signature when a secret is configured."""
    secret = os.getenv("WHATSAPP_WEBHOOK_SECRET", "").strip()
    if not secret:
        return True
    if not signature:
        return False

    expected = "sha256=" + hmac.new(secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


def parse_whatsapp_status_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Extract status details from a Meta WhatsApp status callback payload."""
    statuses = []
    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})
            for status in value.get("statuses", []):
                statuses.append(status)

    if not statuses:
        return {"message_id": "", "status": "", "recipient_id": "", "timestamp": 0}

    latest = statuses[0]
    return {
        "message_id": latest.get("id", ""),
        "status": latest.get("status", ""),
        "recipient_id": latest.get("recipient_id", ""),
        "timestamp": latest.get("timestamp", 0),
        "conversation": latest.get("conversation", {}),
        "pricing": latest.get("pricing", {}),
    }


def whatsapp_webhook(request):
    """Handle Meta WhatsApp webhook callbacks for delivery/read status tracking."""
    if request.method == "GET":
        mode = request.GET.get("hub.mode")
        token = request.GET.get("hub.verify_token")
        challenge = request.GET.get("hub.challenge", "")
        expected = os.getenv("WHATSAPP_WEBHOOK_VERIFY_TOKEN", "").strip()

        if mode == "subscribe" and token and expected and token == expected:
            return HttpResponse(challenge, content_type="text/plain")
        return HttpResponse("Forbidden", status=403)

    if request.method != "POST":
        return HttpResponse("Method not allowed", status=405)

    raw_body = request.body
    signature = request.META.get("HTTP_X_HUB_SIGNATURE_256")
    if not verify_whatsapp_webhook_signature(raw_body, signature):
        return HttpResponse("Forbidden", status=403)

    try:
        payload = json.loads(raw_body.decode("utf-8"))
    except (TypeError, ValueError):
        return HttpResponse("Invalid JSON", status=400)

    status_info = parse_whatsapp_status_payload(payload)
    if status_info["status"]:
        # This is intentionally lightweight; production apps can store or log these events.
        pass

    return JsonResponse({"status": "ok", "message_id": status_info["message_id"], "delivery_status": status_info["status"]})
