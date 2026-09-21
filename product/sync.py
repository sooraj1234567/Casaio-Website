from decimal import Decimal
from typing import Any, Dict


def build_supplier_product_payload(
    name: str,
    description: str,
    supplier_price: str,
    selling_price: str,
    stock: int,
    category_name: str,
    image_url: str = "",
) -> Dict[str, Any]:
    """Map a supplier or marketplace payload into the local Product model shape."""
    return {
        "name": name,
        "description": description,
        "supplier_price": Decimal(str(supplier_price)),
        "selling_price": Decimal(str(selling_price)),
        "stock": int(stock),
        "category_name": category_name,
        "image_url": image_url,
        "is_available": int(stock) > 0,
    }


def build_supplier_feed_url(provider: str) -> str:
    """Return a base endpoint for a supplier feed/service later used by a real API client."""
    providers = {
        "shopify": "https://api.shopify.com",
        "amazon": "https://sellingpartnerapi-na.amazon.com",
        "custom": "https://example-supplier-api.com/products",
    }
    return providers.get(provider.lower(), "https://example-supplier-api.com/products")
