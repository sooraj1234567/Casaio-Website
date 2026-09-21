import os
from typing import Any, Dict, List

import requests
from django.conf import settings
from django.core.mail import send_mail


def get_email_provider() -> str:
    """Return the active transactional email provider (smtp, sendgrid, mailgun)."""
    return (os.getenv("EMAIL_PROVIDER", "smtp") or "smtp").strip().lower()


def build_email_payload(subject: str, recipient: str, message: str, cc: List[str] | None = None) -> Dict[str, Any]:
    """Build a transactional email payload ready for SendGrid/Mailgun or SMTP adapters."""
    return {
        "subject": subject,
        "to": [recipient],
        "cc": cc or [],
        "body": message,
    }


def send_email_notification(subject: str, recipient: str, message: str, cc: List[str] | None = None) -> bool:
    """Send a transactional email using the configured provider or SMTP fallback."""
    if not recipient:
        return False

    payload = build_email_payload(subject, recipient, message, cc)
    provider = get_email_provider()

    if provider == "sendgrid":
        api_key = os.getenv("SENDGRID_API_KEY", "")
        if not api_key:
            provider = "smtp"

    if provider == "mailgun":
        api_key = os.getenv("MAILGUN_API_KEY", "")
        if not api_key:
            provider = "smtp"

    if provider == "sendgrid":
        url = "https://api.sendgrid.com/v3/mail/send"
        headers = {
            "Authorization": f"Bearer {os.getenv('SENDGRID_API_KEY', '')}",
            "Content-Type": "application/json",
        }
        data = {
            "personalizations": [{"to": [{"email": recipient}]}],
            "from": {"email": os.getenv("DEFAULT_FROM_EMAIL", settings.DEFAULT_FROM_EMAIL)},
            "subject": payload["subject"],
            "content": [{"type": "text/plain", "value": payload["body"]}],
        }
        response = requests.post(url, json=data, headers=headers, timeout=15)
        return response.status_code in {200, 201, 202}

    if provider == "mailgun":
        domain = os.getenv("MAILGUN_DOMAIN", "")
        url = f"https://api.mailgun.net/v3/{domain}/messages"
        response = requests.post(
            url,
            auth=("api", os.getenv("MAILGUN_API_KEY", "")),
            data={
                "from": os.getenv("MAILGUN_FROM", settings.DEFAULT_FROM_EMAIL),
                "to": recipient,
                "subject": payload["subject"],
                "text": payload["body"],
            },
            timeout=15,
        )
        return response.status_code in {200, 201, 202}

    send_mail(
        subject=payload["subject"],
        message=payload["body"],
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=payload["to"],
        fail_silently=False,
    )
    return True


def get_sms_provider() -> str:
    """Return the active SMS provider for text notifications."""
    provider = (os.getenv("SMS_PROVIDER", "twilio") or "twilio").strip().lower()
    return provider if provider in {"twilio", "msg91", "custom"} else "twilio"


def build_sms_payload(phone_number: str, message: str) -> Dict[str, Any]:
    """Build a Twilio-style SMS payload ready for a messaging provider."""
    return {
        "to": phone_number,
        "body": message,
    }


def get_whatsapp_provider() -> str:
    """Return the active WhatsApp provider for messaging automation."""
    provider = (os.getenv("WHATSAPP_PROVIDER", "meta") or "meta").strip().lower()
    return provider if provider in {"meta", "twilio", "custom"} else "meta"


def build_whatsapp_payload(
    phone_number: str,
    template_name: str,
    parameters: List[str] | None = None,
    **extra_fields: Any,
) -> Dict[str, Any]:
    """Build a WhatsApp template payload ready for Twilio/Meta provider APIs."""
    payload = {
        "to": phone_number,
        "template_name": template_name,
        "parameters": parameters or [],
    }
    payload.update(extra_fields)
    return payload


def format_whatsapp_number(phone_number: str) -> str:
    """Normalize a local Indian phone number to the WhatsApp format with country code."""
    if not phone_number:
        return ""

    digits = "".join(ch for ch in str(phone_number) if ch.isdigit())
    if not digits:
        return ""

    if digits.startswith("00"):
        digits = digits[2:]
    if digits.startswith("91") and len(digits) > 10:
        return f"+{digits}"
    if len(digits) == 10:
        return f"+91{digits}"
    if digits.startswith("0"):
        digits = digits[1:]
        return f"+91{digits}" if len(digits) == 10 else f"+{digits}"
    return f"+{digits}"


def send_order_whatsapp_notification(phone_number: str, order_number: str, template_name: str, amount: str = "") -> bool:
    """Send a standard order-themed WhatsApp notification using the configured template."""
    phone = format_whatsapp_number(phone_number)
    if not phone:
        return False

    parameters = [order_number]
    if amount:
        parameters.append(amount)

    return send_whatsapp_notification(
        phone_number=phone,
        template_name=template_name,
        parameters=parameters,
    )


def send_whatsapp_notification(
    phone_number: str,
    template_name: str,
    parameters: List[str] | None = None,
    language_code: str = "en",
) -> bool:
    """Send a WhatsApp template message using Meta's Graph API when credentials are configured."""
    if not phone_number or not template_name:
        return False

    access_token = os.getenv("WHATSAPP_ACCESS_TOKEN", "").strip()
    phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "").strip()
    if not access_token or not phone_number_id:
        return False

    payload = build_whatsapp_payload(
        phone_number=phone_number,
        template_name=template_name,
        parameters=parameters or [],
        language_code=language_code,
    )

    url = (
        f"https://graph.facebook.com/v19.0/{phone_number_id}/messages"
    )
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    data = {
        "messaging_product": "whatsapp",
        "to": payload["to"].replace("+", ""),
        "type": "template",
        "template": {
            "name": payload["template_name"],
            "language": {"code": payload.get("language_code", language_code)},
            "components": [
                {
                    "type": "body",
                    "parameters": [{"type": "text", "text": p} for p in payload["parameters"]],
                }
            ],
        },
    }

    response = requests.post(url, headers=headers, json=data, timeout=20)
    return response.status_code in {200, 201, 202}
