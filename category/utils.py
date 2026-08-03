from .models import Category
from django.db.models import Count


def get_category_choices():
    """
    Returns categories in hierarchical order.
    """

    choices = []

    def add_children(parent=None, level=0):

        categories = Category.objects.filter(parent=parent).order_by("name")

        for category in categories:

            category.level = level
            choices.append(category)

            add_children(category, level + 1)

    add_children()

    return choices

def get_category_tree():
    """
    Returns categories in hierarchical order.
    Adds a temporary `level` attribute to each category.
    """

    ordered = []

    def add_children(parent=None, level=0):

        categories = (
            Category.objects
            .filter(parent=parent)
            .annotate(product_count=Count("products"))
            .order_by("name")
        )

        for category in categories:

            category.level = level

            ordered.append(category)

            add_children(category, level + 1)

    add_children()

    return ordered


def get_category_choices():
    return get_category_tree()