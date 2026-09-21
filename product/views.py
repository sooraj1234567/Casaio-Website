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
from accounts.decorators import seller_required
from .form import ProductForm
from .csv_import import sync_csv_feed_to_products


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


@seller_required
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


@seller_required
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


@seller_required
def add_product(request):
    form = ProductForm(request.POST or None, request.FILES or None)

    if form.is_valid():
        product = form.save(commit=False)
        product.seller = request.user
        product.save()
        messages.success(request, f"Product '{product.name}' added successfully.")
        return redirect("seller_products")

    return render(request, "seller/add_product.html", {"form": form})


@seller_required
def seller_csv_import(request):
    if request.method == "POST":
        csv_file = request.FILES.get("csv_file")
        if not csv_file:
            messages.error(request, "Please upload a CSV file.")
            return redirect("seller_csv_import")

        try:
            result = sync_csv_feed_to_products(csv_file, seller=request.user)
            messages.success(
                request,
                f"CSV import complete: {result['created']} created, {result['updated']} updated.",
            )
            return redirect("seller_products")
        except ValueError as exc:
            messages.error(request, str(exc))

    return render(request, "seller/csv_import.html")


@seller_required
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


@seller_required
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


@seller_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if not request.user.is_superuser and product.seller != request.user:
        messages.error(request, "You do not have permission to edit this product.")
        return redirect("seller_products")

    form = ProductForm(
        request.POST or None,
        request.FILES or None,
        instance=product,
    )

    if form.is_valid():
        form.save()
        messages.success(request, f"Product '{product.name}' updated successfully.")
        return redirect("seller_products")

    return render(request, "seller/edit_product.html", {"form": form, "product": product})


@seller_required
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


@seller_required
def seller_reviews(request):
    if request.user.is_superuser:
        reviews = Review.objects.all().select_related("product", "user").order_by("-created_at")
    else:
        reviews = Review.objects.filter(product__seller=request.user).select_related("product", "user").order_by("-created_at")

    return render(request, "seller/seller_reviews.html", {"reviews": reviews})