import os
from typing import Any, Dict, List


def get_analytics_provider() -> str:
    """Return the active analytics provider for tracking and ads data."""
    provider = (os.getenv("ANALYTICS_PROVIDER", "ga4") or "ga4").strip().lower()
    return provider if provider in {"ga4", "meta", "custom"} else "ga4"


def build_ga4_event(event_name: str, params: Dict[str, Any], user_id: str = "") -> Dict[str, Any]:
    """Build a GA4-style event payload ready for a live tracking connector."""
    payload = {
        "name": event_name,
        "params": dict(params or {}),
    }
    if user_id:
        payload["user_id"] = user_id
    return payload


def build_meta_pixel_event(
    event_name: str,
    value: float | int = 0,
    currency: str = "INR",
    content_ids: List[str] | None = None,
    **extra_fields: Any,
) -> Dict[str, Any]:
    """Build a Meta Pixel/Facebook Ads event payload ready for real integration."""
    payload = {
        "event_name": event_name,
        "value": float(value or 0),
        "currency": currency,
        "content_ids": content_ids or [],
    }
    payload.update(extra_fields)
    return payload


def build_ads_campaign_summary(
    campaign_name: str,
    spend: float,
    clicks: int,
    conversions: int,
    revenue: float,
) -> Dict[str, Any]:
    """Compute a lightweight ads summary that is ready for a dashboard or live provider export."""
    roas = (revenue / spend) if spend else 0.0
    cpc = (spend / clicks) if clicks else 0.0
    cpa = (spend / conversions) if conversions else 0.0

    return {
        "campaign_name": campaign_name,
        "spend": float(spend),
        "clicks": int(clicks),
        "conversions": int(conversions),
        "revenue": float(revenue),
        "roas": round(roas, 2),
        "cpc": round(cpc, 2),
        "cpa": round(cpa, 2),
    }


def get_google_ads_client() -> Dict[str, Any]:
    """Return stub metadata for a future Google Ads client integration."""
    return {
        "provider": "google_ads",
        "stub": True,
        "customer_id": os.getenv("GOOGLE_ADS_CUSTOMER_ID", "123-456-7890"),
        "developer_token": os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN", "stub-token"),
        "status": "not_connected",
    }


def build_google_ads_conversion(
    conversion_name: str,
    value: float | int = 0,
    currency: str = "INR",
    order_id: str = "",
    **extra_fields: Any,
) -> Dict[str, Any]:
    """Create a Google Ads conversion payload for a future API call."""
    payload = {
        "conversion_name": conversion_name,
        "value": float(value or 0),
        "currency": currency,
        "order_id": order_id,
    }
    payload.update(extra_fields)
    return payload


def get_meta_ads_client() -> Dict[str, Any]:
    """Return stub metadata for a future Meta Ads client integration."""
    return {
        "provider": "meta_ads",
        "stub": True,
        "pixel_id": os.getenv("META_PIXEL_ID", "stub-pixel-id"),
        "access_token": os.getenv("META_ACCESS_TOKEN", "stub-access-token"),
        "status": "not_connected",
    }


def build_meta_ads_event(
    event_name: str,
    value: float | int = 0,
    currency: str = "INR",
    content_ids: List[str] | None = None,
    **extra_fields: Any,
) -> Dict[str, Any]:
    """Create a Meta Ads event payload for a future API request."""
    payload = {
        "event_name": event_name,
        "value": float(value or 0),
        "currency": currency,
        "content_ids": content_ids or [],
    }
    payload.update(extra_fields)
    return payload
