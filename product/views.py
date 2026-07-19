from django.shortcuts import render, get_object_or_404
from .models import Product
from category.models import Category
from django.core.paginator import Paginator


def product_list(request):
    products = Product.objects.filter(
        is_available=True
    ).select_related("category")

    main_categories = Category.objects.filter(
        parent__isnull=True,
        is_active=True
    )

    sub_categories = Category.objects.filter(
        parent__isnull=False,
        is_active=True
    )

    search = request.GET.get("search")

    if search:
        products = products.filter(name__icontains=search)

    category = request.GET.get("category")
        
    if category:
        products = products.filter(category__slug=category)

    sort = request.GET.get("sort")
    
    if sort == "low":
        products = products.order_by("price")

    elif sort == "high":
        products = products.order_by("-price")
    
    elif sort == "new":
        products = products.order_by("-created_at")

    paginator = Paginator(products, 10)

    page_number = request.GET.get("page")

    page_obj = paginator.get_page(page_number)

    context = {
        "products": products,
        "page_obj": page_obj,
        "main_categories": main_categories,
        "sub_categories": sub_categories,
        "search": search,
        "selected_category": category,
        "sort": sort,
    }

    return render(
        request,
        "product/product_list.html",
        {
            "products": products
        }
    )

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_available=True)

    return render(
        request,
        "product/product_detail.html",
        {
            "product": product
        }
    )