from django.shortcuts import render, get_object_or_404
from .models import Category


def category_list(request):
    categories = Category.objects.filter(parent__isnull=True, is_active=True).order_by("name")

    return render(
        request,
        "category/category_list.html",
        {"categories": categories},
    )


def category_detail(request, slug):
    category = get_object_or_404(
        Category,
        slug=slug,
        is_active=True
    )

    subcategories = category.subcategories.filter(
        is_active=True
    ).order_by("name")

    return render(
        request,
        "category/category_detail.html",
        {
            "category": category,
            "subcategories": subcategories,
        }
    )