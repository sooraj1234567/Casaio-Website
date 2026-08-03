from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.core.paginator import Paginator
from django.db.models import Q
from django.db.models import Count
from django.utils import timezone
from django.contrib import messages

from orders.models import Order
from product.models import Product, ProductImage
from product.form import ProductForm
from category.models import Category
from category.forms import CategoryForm
from category.utils import get_category_tree


User = get_user_model()


def dashboard(request):

    total_revenue = (
        Order.objects.filter(
            payment_status=True,
            status="delivered"
        ).aggregate(
            total=Sum("total")
        )["total"] or 0
    )

    total_orders = Order.objects.count()

    total_customers = User.objects.filter(is_staff=False).count()

    total_products = Product.objects.count()

    recent_orders = Order.objects.order_by("-created_at")[:5]

    context = {
        "total_revenue": total_revenue,
        "total_orders": total_orders,
        "total_customers": total_customers,
        "total_products": total_products,
        "recent_orders": recent_orders,
    }

    return render(request, "dashboard/dashboard.html", context)

def order_list(request):

    search = request.GET.get("search", "")

    status = request.GET.get("status", "")

    orders = (
        Order.objects
        .select_related("user")
        .order_by("-created_at")
    )

    if search:
        
        orders = orders.filter(
            Q(user__username__icontains=search) |
            Q(order_number__icontains=search) 
        )

    if status:
        orders = orders.filter(status=status)

    paginator = Paginator(orders, 10)

    page = request.GET.get("page")

    orders = paginator.get_page(page)

    return render(
        request,
        "dashboard/orders/order_list.html",
        {
            "orders": orders,
            "search": search,
            "status": status,
        }
    )

def order_detail(request, pk):

    order = get_object_or_404(
        Order.objects.select_related(
            "user",
            "address"
        ).prefetch_related("items__product"),
        pk=pk
    )

    context = {
        "order": order,
    }

    return render(
        request,
        "dashboard/orders/order_detail.html",
        context,
    )

def update_order_status(request, pk):

    order = get_object_or_404(Order, pk=pk)

    if request.method == "POST":

        status = request.POST.get("status")

        if status in dict(Order.STATUS_CHOICES):

            order.status = status

            if status == "cancelled":
                order.cancelled_at = timezone.now()

            else:
                order.cancelled_at = None

            order.save()

    return redirect("dashboard:order_detail", pk=pk)

def product_list(request):

    search = request.GET.get("search", "")

    products = (
        Product.objects
        .select_related("category")
        .order_by("-created_at")
    )

    if search:
        products = products.filter(
            Q(name__icontains=search) |
            Q(category__name__icontains=search)
        )

    paginator = Paginator(products, 10)

    page = request.GET.get("page")

    products = paginator.get_page(page)

    context = {
        "products": products,
        "search": search,
    }

    return render(
        request,
        "dashboard/products/product_list.html",
        context,
    )

def product_create(request):

    if request.method == "POST":

        form = ProductForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            product = form.save(commit=False)

            # Automatically calculate discount percentage
            if (
                product.offer_price
                and product.offer_price < product.selling_price
            ):
                product.discount_percentage = int(
                    (
                        (product.selling_price - product.offer_price)
                        / product.selling_price
                    ) * 100
                ) 
            else:
                product.discount_percentage = 0

            product.save()

            gallery_images = request.FILES.getlist("gallery_images")

            for image in gallery_images:

                ProductImage.objects.create(
                    product=product,
                    image=image
                )

            return redirect("dashboard:product_list")

    else:

        form = ProductForm()

    return render(
        request,
        "dashboard/products/product_create.html",
        {
            "form": form
        }
    )

def product_update(request, pk):

    product = get_object_or_404(Product, pk=pk)

    gallery_images = ProductImage.objects.filter(product=product)


    if request.method == "POST":

        form = ProductForm(
            request.POST,
            request.FILES,
            instance=product
        )

        if form.is_valid():

            product = form.save()

            uploaded_images = request.FILES.getlist("gallery_images")

            for image in uploaded_images:

                ProductImage.objects.create(
                    product=product,
                    image=image
                )

            messages.success(
                request,
                "Product updated successfully."
            )

            return redirect("dashboard:product_list")

    else:

        form = ProductForm(instance=product)

    return render(
        request,
        "dashboard/products/product_update.html",
        {
            "form": form,
            "product": product,
            "gallery_images": gallery_images,
        }
    )

def delete_gallery_image(request, pk):

    image = get_object_or_404(ProductImage, pk=pk)

    product_id = image.product.id

    image.delete()

    messages.success(
        request,
        "Gallery image deleted successfully."
    )

    return redirect(
        "dashboard:product_update",
        pk=product_id
    )

def product_delete(request, pk):

    product = get_object_or_404(Product, pk=pk)

    if request.method == "POST":

        product_name = product.name

        product.delete()

        messages.success(
            request,
            f'"{product_name}" has been deleted successfully.'
        )

    return redirect("dashboard:product_list")

def category_list(request):

    search = request.GET.get("search", "")

    categories = get_category_tree()

    if search:

        categories = [
            category
            for category in categories
            if search.lower() in category.name.lower()
        ]

    paginator = Paginator(categories, 10)

    page_number = request.GET.get("page")

    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "dashboard/category/category_list.html",
        {
            "page_obj": page_obj,
            "search": search,
        }
    )

def category_create(request):

    if request.method == "POST":

        form = CategoryForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Category added successfully."
            )

            return redirect("dashboard:category_list")

    else:

        form = CategoryForm()

    return render(
        request,
        "dashboard/category/category_create.html",
        {
            "form": form,
        }
    )

def category_update(request, pk):

    category = get_object_or_404(Category, pk=pk)

    if request.method == "POST":

        form = CategoryForm(
            request.POST,
            request.FILES,
            instance=category
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Category updated successfully."
            )

            return redirect("dashboard:category_list")

    else:

        form = CategoryForm(instance=category)

    return render(
        request,
        "dashboard/category/category_update.html",
        {
            "form": form,
            "category": category,
        }
    )

def category_delete(request, pk):

    category = get_object_or_404(Category, pk=pk)

    if request.method == "POST":

        # Check for child categories
        if category.subcategories.exists():

            messages.error(
                request,
                "Cannot delete this category because it has subcategories."
            )

            return redirect("dashboard:category_list")

        # Check for assigned products
        if category.products.exists():

            messages.error(
                request,
                "Cannot delete this category because products are assigned to it."
            )

            return redirect("dashboard:category_list")

        category_name = category.name

        category.delete()

        messages.success(
            request,
            f'"{category_name}" deleted successfully.'
        )

    return redirect("dashboard:category_list")