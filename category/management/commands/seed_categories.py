from django.core.management.base import BaseCommand
from category.models import Category
from django.utils.text import slugify

CATEGORY_TREE = {

    "Furniture": {

        "Living Room": [
            "Sofas",
            "Sectional Sofas",
            "Coffee Tables",
            "TV Units",
            "Side Tables",
            "Console Tables",
            "Lounge Chairs",
            "Bookshelves",
        ],

        "Bedroom": [
            "Beds",
            "Bed Frames",
            "Mattresses",
            "Wardrobes",
            "Bedside Tables",
            "Dressers",
            "Chest of Drawers",
            "Vanity Tables",
        ],

        "Dining Room": [
            "Dining Tables",
            "Dining Chairs",
            "Dining Benches",
            "Bar Stools",
            "Sideboards",
        ],

        "Office": [
            "Office Chairs",
            "Office Desks",
            "Computer Tables",
            "Bookshelves",
            "Filing Cabinets",
        ],

        "Outdoor Furniture": [
            "Garden Chairs",
            "Garden Tables",
            "Patio Sets",
            "Hammocks",
        ],

    },

    "Kitchen Accessories": {

        "Cookware": [
            "Frying Pans",
            "Saucepans",
            "Pressure Cookers",
            "Woks",
        ],

        "Bakeware": [
            "Baking Trays",
            "Cake Moulds",
            "Oven Dishes",
        ],

        "Kitchen Tools": [
            "Peelers",
            "Graters",
            "Whisks",
            "Tongs",
        ],

        "Knife Sets": [],
        "Cutting Boards": [],
        "Dinnerware": [],
        "Drinkware": [],
        "Food Storage": [],
        "Kitchen Organisers": [],

    },

    "Home Decor": {

        "Wall Art": [],
        "Mirrors": [],
        "Clocks": [],
        "Rugs": [],
        "Curtains": [],
        "Cushions": [],
        "Throws": [],
        "Artificial Plants": [],
        "Vases": [],
        "Candles": [],
        "Photo Frames": [],
        "Decorative Accessories": [],
        "Indoor Plants": [],

    },

    "Storage": {

        "Storage Boxes": [],
        "Storage Baskets": [],
        "Wardrobe Organisers": [],
        "Shoe Racks": [],
        "Shelves": [],
        "Cabinets": [],
        "Laundry Baskets": [],
        "Drawer Organisers": [],
        "Kitchen Storage": [],
        "Bathroom Storage": [],

    },

    "Lighting": {

        "Ceiling Lights": [],
        "Pendant Lights": [],
        "Chandeliers": [],
        "Table Lamps": [],
        "Floor Lamps": [],
        "Wall Lights": [],
        "Desk Lamps": [],
        "LED Lights": [],
        "Outdoor Lighting": [],
        "Smart Lighting": [],

    },

}

class Command(BaseCommand):
    help = "Seed Casaio categories"

    def create_category(self, name, parent=None):

        if parent:
            slug = slugify(f"{parent.slug}-{name}")
        else:
            slug = slugify(name)

        category, created = Category.objects.update_or_create(
            slug=slug,
            defaults={
                "name": name,
                "parent": parent,
                "description": f"{name} category",
                "is_active": True,
            },
        )

        if created:
            self.stdout.write(
                self.style.SUCCESS(f"✓ Created: {name}")
            )
        else:
            self.stdout.write(
                self.style.WARNING(f"↺ Updated: {name}")
            )

        return category

    def handle(self, *args, **options):

        for root_name, children in CATEGORY_TREE.items():

            root = self.create_category(root_name)

            for child_name, grandchildren in children.items():

                child = self.create_category(
                    child_name,
                    parent=root
                )

                for grandchild_name in grandchildren:

                    self.create_category(
                        grandchild_name,
                        parent=child
                    )

        self.stdout.write(
            self.style.SUCCESS(
                "\n🎉 Casaio categories seeded successfully!"
            )
        )