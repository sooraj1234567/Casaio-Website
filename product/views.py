from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator

from .models import Product
from category.models import Category
from wishlist.models import Wishlist
from reviews.models import Review
from reviews.forms import ReviewForm
from django.db.models import Avg


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

    wishlist_product_ids = []

    if request.user.is_authenticated:
        wishlist_product_ids = Wishlist.objects.filter(
            user=request.user
        ).values_list("product_id", flat=True)

    paginator = Paginator(products, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "products": page_obj,
        "page_obj": page_obj,
        "main_categories": main_categories,
        "sub_categories": sub_categories,
        "search": search,
        "selected_category": category,
        "sort": sort,
        "wishlist_product_ids": wishlist_product_ids,
    }

    return render(
        request,
        "product/product_list.html",
        context
    )

def product_detail(request, slug):

    product = get_object_or_404(
        Product,
        slug=slug,
        is_available=True
    )

    reviews = Review.objects.filter(
        product=product
    ).select_related("user")

    user_review = None

    if request.user.is_authenticated:

        user_review = reviews.filter(
            user=request.user
        ).first()

    review_form = ReviewForm(
        instance=user_review
    )

    average_rating = reviews.aggregate(
        Avg("rating")
    )["rating__avg"] or 0

    rating_counts = {}

    for i in range(5, 0, -1):

        rating_counts[i] = reviews.filter(
            rating=i
        ).count()

    related_products = Product.objects.filter(
        category=product.category,
        is_available=True
    ).exclude(
        id=product.id
    )[:4]

    variants = product.variants.all()

    in_stock = product.stock > 10
    low_stock = 0 < product.stock <= 10
    out_of_stock = product.stock == 0

    return render(
        request,
        "product/product_detail.html",
        {
            "product": product,
            "reviews": reviews,
            "review_form": review_form,
            "average_rating": average_rating,
            "rating_counts": rating_counts,
            "related_products": related_products,
            "variants": variants,
            "in_stock": in_stock,
            "low_stock": low_stock,
            "out_of_stock": out_of_stock,
        }
    )