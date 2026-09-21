import re
from typing import Dict, Any


def validate_delivery_location(city: str, state: str, pincode: str) -> Dict[str, Any]:
    """Validate a delivery location for Indian shipping before checkout. This is a lightweight local validation layer that can later be replaced by Google Maps/India PIN APIs."""
    clean_city = (city or "").strip()
    clean_state = (state or "").strip()
    clean_pincode = (pincode or "").strip()

    is_valid_pincode = bool(re.fullmatch(r"\d{6}", clean_pincode))
    has_city = bool(clean_city)
    has_state = bool(clean_state)

    return {
        "is_valid": is_valid_pincode and has_city and has_state,
        "country": "India",
        "city": clean_city,
        "state": clean_state,
        "pincode": clean_pincode,
        "message": "Valid delivery location." if is_valid_pincode and has_city and has_state else "Invalid city/state/pincode.",
    }


def get_geo_lookup_url(pincode: str) -> str:
    """Return the configured Geocoding/lookup service URL for future integration."""
    return f"https://postalpincode.in/api/pincode/{pincode}"
