from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db.models import Avg, Sum
from django.db.models.functions import TruncMonth

from .models import Product
from category.models import Category
from wishlist.models import Wishlist
from reviews.models import Review
from reviews.forms import ReviewForm
from orders.models import OrderItem


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
        products = products.order_by("selling_price")

    elif sort == "high":
        products = products.order_by("-selling_price")

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


@login_required
def seller_dashboard(request):
    if request.user.is_superuser:
        products = Product.objects.all().order_by("-created_at")
        order_items = OrderItem.objects.all().select_related("order", "product", "order__user").order_by("-order__created_at")
    else:
        products = Product.objects.filter(seller=request.user).order_by("-created_at")
        order_items = OrderItem.objects.filter(product__seller=request.user).select_related("order", "product", "order__user").order_by("-order__created_at")

    total_products = products.count()
    total_orders = order_items.values("order").distinct().count()

    monthly_sales = (
        order_items.filter(status="delivered")
        .annotate(month=TruncMonth("order__created_at"))
        .values("month")
        .annotate(total=Sum("selling_price"))
        .order_by("month")
    )

    chart_labels = [entry["month"].strftime("%b %Y") for entry in monthly_sales if entry["month"]]
    chart_data = [float(entry["total"]) for entry in monthly_sales if entry["month"]]

    context = {
        "products": products,
        "order_items": order_items,
        "total_products": total_products,
        "total_orders": total_orders,
        "chart_labels": chart_labels,
        "chart_data": chart_data,
    }

    return render(request, "seller/dashboard.html", context)


@login_required
def seller_products(request):
    if request.user.is_superuser:
        products = Product.objects.all().order_by("-created_at")
    else:
        products = Product.objects.filter(seller=request.user).order_by("-created_at")

    return render(
        request,
        "seller/seller_products.html",
        {"products": products}
    )


@login_required
def add_product(request):
    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")
        selling_price = request.POST.get("selling_price")
        stock = request.POST.get("stock", 0)
        category_id = request.POST.get("category")
        image = request.FILES.get("image")

        category = get_object_or_404(Category, id=category_id) if category_id else None

        product = Product.objects.create(
            seller=request.user,
            name=name,
            description=description,
            selling_price=selling_price,
            stock=stock,
            category=category,
            image=image,
            is_available=True
        )
        messages.success(request, f"Product '{product.name}' added successfully.")
        return redirect("seller_products")

    categories = Category.objects.filter(is_active=True)
    return render(request, "seller/add_product.html", {"categories": categories})


@login_required
def seller_inventory(request):
    if request.user.is_superuser:
        products = Product.objects.all().order_by("stock")
    else:
        products = Product.objects.filter(seller=request.user).order_by("stock")

    return render(
        request,
        "seller/inventory.html",
        {"products": products}
    )


@login_required
@require_POST
def update_stock(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if not request.user.is_superuser and product.seller != request.user:
        messages.error(request, "You do not have permission to update this stock.")
        return redirect("seller_inventory")

    try:
        new_stock = int(request.POST.get("stock", 0))
        if new_stock >= 0:
            product.stock = new_stock
            product.save()
            messages.success(request, f"Stock updated successfully for {product.name}.")
        else:
            messages.error(request, "Stock cannot be negative.")
    except ValueError:
        messages.error(request, "Invalid stock value.")

    return redirect("seller_inventory")


@login_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if not request.user.is_superuser and product.seller != request.user:
        messages.error(request, "You do not have permission to edit this product.")
        return redirect("seller_products")

    if request.method == "POST":
        product.name = request.POST.get("name", product.name)
        product.description = request.POST.get("description", product.description)
        product.selling_price = request.POST.get("selling_price", product.selling_price)
        product.stock = request.POST.get("stock", product.stock)
        
        if "image" in request.FILES:
            product.image = request.FILES["image"]

        product.save()
        messages.success(request, f"Product '{product.name}' updated successfully.")
        return redirect("seller_products")

    return render(request, "seller/edit_product.html", {"product": product})


@login_required
@require_POST
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if not request.user.is_superuser and product.seller != request.user:
        messages.error(request, "You do not have permission to delete this product.")
        return redirect("seller_products")

    product_name = product.name
    product.delete()
    messages.success(request, f"Product '{product_name}' has been deleted.")
    return redirect("seller_products")


@login_required
def seller_reviews(request):
    if request.user.is_superuser:
        reviews = Review.objects.all().select_related("product", "user").order_by("-created_at")
    else:
        reviews = Review.objects.filter(product__seller=request.user).select_related("product", "user").order_by("-created_at")

    return render(request, "seller/seller_reviews.html", {"reviews": reviews})