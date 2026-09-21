import csv
from decimal import Decimal
from pathlib import Path
from typing import Dict, List

from django.core.files.base import ContentFile

from category.models import Category
from product.models import Product


REQUIRED_COLUMNS = {
    "name",
    "description",
    "supplier_price",
    "selling_price",
    "stock",
    "category_name",
}


def parse_csv_feed(file_obj) -> List[Dict[str, str]]:
    """Read a CSV supplier feed into row dictionaries."""
    file_obj.seek(0)
    reader = csv.DictReader(file_obj.read().decode("utf-8-sig").splitlines())
    return list(reader)


def validate_csv_columns(row_headers: List[str]) -> List[str]:
    missing = sorted(REQUIRED_COLUMNS - set(row_headers))
    return missing


def sync_csv_feed_to_products(file_obj, seller=None) -> Dict[str, int]:
    """Import a supplier CSV feed into the local product catalog."""
    rows = parse_csv_feed(file_obj)
    if not rows:
        return {"created": 0, "updated": 0, "skipped": 0}

    headers = list(rows[0].keys())
    missing_columns = validate_csv_columns(headers)
    if missing_columns:
        raise ValueError(f"Missing required CSV columns: {', '.join(missing_columns)}")

    created = 0
    updated = 0

    for row in rows:
        name = (row.get("name") or "").strip()
        if not name:
            continue

        category_name = (row.get("category_name") or "General").strip() or "General"
        category, _ = Category.objects.get_or_create(name=category_name)

        supplier_price = Decimal(str(row.get("supplier_price") or "0"))
        selling_price = Decimal(str(row.get("selling_price") or "0"))
        stock = int(row.get("stock") or 0)

        product, product_created = Product.objects.get_or_create(
            name=name,
            defaults={
                "seller": seller,
                "category": category,
                "description": row.get("description") or "",
                "supplier_price": supplier_price,
                "selling_price": selling_price,
                "stock": stock,
                "is_available": stock > 0,
                "image": ContentFile(b"", name=f"{name.lower().replace(' ', '_')}.jpg"),
            },
        )

        if product_created:
            created += 1
        else:
            product.seller = seller or product.seller
            product.category = category
            product.description = row.get("description") or product.description
            product.supplier_price = supplier_price
            product.selling_price = selling_price
            product.stock = stock
            product.is_available = stock > 0
            product.save()
            updated += 1

    return {"created": created, "updated": updated, "skipped": max(len(rows) - created - updated, 0)}
