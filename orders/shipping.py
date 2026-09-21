import os
from typing import Any, Dict


def build_shiprocket_payload(
    order_number: str,
    customer_name: str,
    phone: str,
    address_line: str,
    city: str,
    state: str,
    pincode: str,
    amount: str,
    product_name: str,
    product_sku: str = "",
    payment_method: str = "Prepaid",
    weight_kg: float = 0.5,
) -> Dict[str, Any]:
    """Construct a Shiprocket-compatible payload for a shipment order."""
    return {
        "order_id": order_number,
        "order_date": "",
        "pickup_location": os.getenv("SHIPROCKET_PICKUP_LOCATION", "Default Pickup"),
        "channel_id": os.getenv("SHIPROCKET_CHANNEL_ID", ""),
        "comment": "Casaio order",
        "billing_customer_name": customer_name,
        "billing_last_name": "",
        "billing_address": address_line,
        "billing_address_2": "",
        "billing_city": city,
        "billing_pincode": pincode,
        "billing_state": state,
        "billing_country": "India",
        "billing_email": "",
        "billing_phone": phone,
        "shipping_is_billing": True,
        "shipping_customer_name": customer_name,
        "shipping_last_name": "",
        "shipping_address": address_line,
        "shipping_address_2": "",
        "shipping_city": city,
        "shipping_pincode": pincode,
        "shipping_state": state,
        "shipping_country": "India",
        "shipping_email": "",
        "shipping_phone": phone,
        "order_items": [
            {
                "name": product_name,
                "sku": product_sku or product_name[:20],
                "units": 1,
                "selling_price": amount,
                "discount": "0",
                "tax": "0",
                "hsn": "",
            }
        ],
        "payment_method": payment_method,
        "shipping_charges": "0",
        "giftwrap_charges": "0",
        "transaction_charges": "0",
        "total_discount": "0",
        "sub_total": amount,
        "length": "10",
        "breadth": "10",
        "height": "10",
        "weight": str(weight_kg),
    }


def get_shiprocket_auth_token() -> str:
    """Return a token from environment variables when configured."""
    return os.getenv("SHIPROCKET_API_KEY", "")


def get_shiprocket_base_url() -> str:
    """Return the API base URL for Shiprocket environment configuration."""
    return os.getenv("SHIPROCKET_BASE_URL", "https://apiv2.shiprocket.in")
