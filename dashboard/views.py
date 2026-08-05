from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.core.paginator import Paginator
from django.db.models import Q
from django.db.models import Count
from django.utils import timezone
from django.contrib import messages
from django.http import HttpResponse
from datetime import timedelta, datetime

from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

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

    payment = request.GET.get("payment", "")

    date_filter = request.GET.get("date", "")

    orders = (
        Order.objects
        .select_related("user")
        .prefetch_related("items")
        .order_by("-created_at")
    )

    if search:
        
        orders = orders.filter(
            Q(user__username__icontains=search) |
            Q(order_number__icontains=search) 
        )

    if status:
        orders = orders.filter(status=status)

    if payment:
        orders = orders.filter(payment_method=payment)

    today = timezone.now().date()

    if date_filter == "today":

        orders = orders.filter(
            created_at__date=today
        )

    elif date_filter == "week":

        orders = orders.filter(
            created_at__date__gte=today - timedelta(days=7)
        )

    elif date_filter == "month":

        orders = orders.filter(
            created_at__month=today.month,
            created_at__year=today.year,
        )

    elif date_filter == "year":

        orders = orders.filter(
            created_at__year=today.year
        )

    paginator = Paginator(orders, 10)

    page = request.GET.get("page")

    orders = paginator.get_page(page)

    total_orders = Order.objects.count()

    pending_orders = Order.objects.filter(
        status="pending"
    ).count()

    delivered_orders = Order.objects.filter(
        status="delivered"
    ).count()

    total_revenue = (
        Order.objects.filter(
            payment_status=True,
            status="delivered"
        ).aggregate(
            total=Sum("total")
        )["total"] or 0
    )

    return render(
        request,
        "dashboard/orders/order_list.html",
        {
            "orders": orders,
            "search": search,
            "status": status,
            "payment": payment,
            "date_filter": date_filter,
            "total_orders": total_orders,
            "pending_orders": pending_orders,
            "delivered_orders": delivered_orders,
            "total_revenue": total_revenue,
        }
    )

def export_orders_excel(request):

    search = request.GET.get("search", "")
    status = request.GET.get("status", "")
    payment = request.GET.get("payment", "")
    date_filter = request.GET.get("date", "")

    orders = (
        Order.objects
        .select_related("user")
        .prefetch_related("items")
        .order_by("-created_at")
    )

    if search:

        orders = orders.filter(
            Q(user__username__icontains=search) |
            Q(order_number__icontains=search)
        )

    if status:

        orders = orders.filter(status=status)

    if payment:

        orders = orders.filter(payment_method=payment)

    today = timezone.now().date()

    if date_filter == "today":

        orders = orders.filter(
            created_at__date=today
        )

    elif date_filter == "week":

        orders = orders.filter(
            created_at__date__gte=today - timedelta(days=7)
        )

    elif date_filter == "month":

        orders = orders.filter(
            created_at__month=today.month,
            created_at__year=today.year
        )

    elif date_filter == "year":

        orders = orders.filter(
            created_at__year=today.year
        )

    workbook = Workbook()

    sheet = workbook.active

    sheet.title = "Orders"

    headers = [

        "Order Number",
        "Customer",
        "Items",
        "Date",
        "Payment Method",
        "Payment Status",
        "Order Status",
        "Total"

    ]

    for col, header in enumerate(headers, start=1):

        cell = sheet.cell(row=1, column=col)

        cell.value = header

        cell.font = Font(bold=True)

    row = 2

    for order in orders:

        sheet.cell(row=row, column=1).value = order.order_number

        sheet.cell(row=row, column=2).value = order.user.username

        sheet.cell(row=row, column=3).value = order.items.count()

        sheet.cell(
            row=row,
            column=4
        ).value = order.created_at.strftime("%d-%m-%Y")

        sheet.cell(
            row=row,
            column=5
        ).value = order.get_payment_method_display()

        sheet.cell(
            row=row,
            column=6
        ).value = "Paid" if order.payment_status else "Pending"

        sheet.cell(
            row=row,
            column=7
        ).value = order.get_status_display()

        sheet.cell(
            row=row,
            column=8
        ).value = float(order.total)

        row += 1

    for column_cells in sheet.columns:

        length = max(
            len(str(cell.value))
            if cell.value else 0
            for cell in column_cells
        )

        sheet.column_dimensions[
            column_cells[0].column_letter
        ].width = length + 5

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    filename = datetime.now().strftime("Orders_%d-%m-%Y.xlsx") + "_Orders.xlsx"

    response[
        "Content-Disposition"
    ] = f'attachment; filename="{filename}"'

    workbook.save(response)

    return response

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

def order_invoice(request, pk):

    order = get_object_or_404(
        Order.objects.select_related(
            "user",
            "address"
        ).prefetch_related(
            "items__product"
        ),
        pk=pk
    )

    return render(
        request,
        "dashboard/orders/invoice.html",
        {
            "order": order,
        }
    )

def download_invoice_pdf(request, pk):

    order = get_object_or_404(
        Order.objects.select_related(
            "user",
            "address"
        ).prefetch_related(
            "items__product"
        ),
        pk=pk
    )

    response = HttpResponse(content_type="application/pdf")

    response["Content-Disposition"] = (
        f'attachment; filename="Invoice-{order.order_number}.pdf"'
    )

    doc = SimpleDocTemplate(response)

    styles = getSampleStyleSheet()

    elements = []

    elements.append(
        Paragraph("<b>CASAIO</b>", styles["Title"])
    )

    elements.append(
        Paragraph(
            f"Invoice No: {order.order_number}",
            styles["Normal"]
        )
    )

    elements.append(
        Paragraph(
            f"Date: {order.created_at.strftime('%d %b %Y')}",
            styles["Normal"]
        )
    )

    elements.append(Spacer(1, 20))

    elements.append(
        Paragraph(
            "<b>Bill To</b>",
            styles["Heading2"]
        )
    )

    elements.append(
        Paragraph(
            order.address.full_name,
            styles["Normal"]
        )
    )

    elements.append(
        Paragraph(
            order.address.house_name,
            styles["Normal"]
        )
    )

    elements.append(
        Paragraph(
            order.address.area,
            styles["Normal"]
        )
    )

    elements.append(
        Paragraph(
            f"{order.address.city}, {order.address.state}",
            styles["Normal"]
        )
    )

    elements.append(
        Paragraph(
            order.address.pincode,
            styles["Normal"]
        )
    )

    elements.append(Spacer(1, 20))

    data = [
        [
            "Product",
            "Qty",
            "Price",
            "Total",
        ]
    ]

    for item in order.items.all():

        data.append(
            [
                item.product.name,
                str(item.quantity),
                f"₹{item.price}",
                f"₹{item.total_price}",
            ]
        )

    table = Table(data)

    table.setStyle(

        TableStyle(

            [

                ("BACKGROUND", (0,0), (-1,0), colors.orange),

                ("TEXTCOLOR", (0,0), (-1,0), colors.white),

                ("GRID", (0,0), (-1,-1), 1, colors.grey),

                ("BOTTOMPADDING", (0,0), (-1,0), 12),

                ("BACKGROUND", (0,1), (-1,-1), colors.beige),

            ]

        )

    )

    elements.append(table)

    elements.append(Spacer(1, 25))

    elements.append(

        Paragraph(

            f"<b>Total : ₹{order.total}</b>",

            styles["Heading2"]

        )

    )

    doc.build(elements)

    return response

def bulk_delete_orders(request):

    if request.method == "POST":

        selected_orders = request.POST.getlist(
            "selected_orders"
        )

        deleted_count = Order.objects.filter(
            id__in=selected_orders
        ).count()

        Order.objects.filter(
            id__in=selected_orders
        ).delete()

        messages.success(
            request,
            f"{deleted_count} order(s) deleted successfully."
        )

    return redirect("dashboard:order_list")

def order_delete(request, pk):

    order = get_object_or_404(Order, pk=pk)

    if request.method == "POST":

        order_number = order.order_number

        order.delete()

        messages.success(
            request,
            f'Order "{order_number}" deleted successfully.'
        )

    return redirect("dashboard:order_list")

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

def customer_list(request):

    search = request.GET.get("search", "")

    customers = (
        User.objects
        .filter(is_staff=False)
        .order_by("-date_joined")
    )

    if search:

        customers = customers.filter(

            Q(username__icontains=search) |

            Q(email__icontains=search)

        )

    paginator = Paginator(customers, 10)

    page = request.GET.get("page")

    customers = paginator.get_page(page)

    total_customers = User.objects.filter(
        is_staff=False
    ).count()

    active_customers = User.objects.filter(
        is_staff=False,
        is_active=True
    ).count()

    blocked_customers = User.objects.filter(
        is_staff=False,
        is_active=False
    ).count()

    new_customers = User.objects.filter(
        is_staff=False,
        date_joined__month=timezone.now().month,
        date_joined__year=timezone.now().year,
    ).count()

    return render(
        request,
        "dashboard/customers/customer_list.html",
        {
            "customers": customers,
            "search": search,

            "total_customers": total_customers,
            "active_customers": active_customers,
            "blocked_customers": blocked_customers,
            "new_customers": new_customers,
        },
    )