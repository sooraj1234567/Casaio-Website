from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db import transaction
from django.contrib import messages
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.db.models import Sum
from django.http import HttpResponse

from cart.models import Cart
from checkout.models import Address

from .models import Order, OrderItem, Coupon

import razorpay
from django.conf import settings
import logging
import csv

logger = logging.getLogger(__name__)

client = razorpay.Client(
    auth=(
        settings.RAZORPAY_KEY_ID,
        settings.RAZORPAY_KEY_SECRET
    )
)

@login_required
@transaction.atomic
def place_order(request):

    if request.method != "POST":
        return redirect("checkout:checkout")

    cart = get_object_or_404(
        Cart,
        user=request.user
    )

    if not cart.items.exists():
        return redirect("cart:cart_page")

    address = Address.objects.filter(
        user=request.user,
        is_default=True
    ).first()

    if not address:
        return redirect("checkout:checkout")

    payment_method = request.POST.get("payment_method", "cod")

    subtotal = 0

    for item in cart.items.all():
        subtotal += item.product.selling_price * item.quantity

    order = Order.objects.create(
        user=request.user,
        address=address,
        payment_method=payment_method,
        subtotal=subtotal,
        total=subtotal,
        payment_status=False,
        status="pending",
    )

    for item in cart.items.all():
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            selling_price=item.product.selling_price,
        )

    if payment_method == "cod":

        order.payment_status = False  # COD starts unpaid until delivered
        order.status = "pending"      # Start as pending until the seller updates it
        order.save()

        cart.items.all().delete()

        return redirect(
            "orders:order_success",
            order_id=order.id
        )

    elif payment_method == "razorpay":

        amount = int(order.total * 100)

        try:
            razorpay_order = client.order.create({
                "amount": amount,
                "currency": "INR",
                "payment_capture": 1
            })

            order.razorpay_order_id = razorpay_order["id"]
            order.save()

            return render(
                request,
                "payments/payment.html",
                {
                    "order": order,
                    "razorpay_order": razorpay_order,
                    "razorpay_key": settings.RAZORPAY_KEY_ID,
                }
            )

        except Exception as e:
            logger.error(f"Razorpay order creation failed: {str(e)}")
            order.delete()
            return redirect("checkout:checkout")

    else:
        return redirect("checkout:checkout")

@login_required
def order_success(request, order_id):

    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    return render(
        request,
        "orders/order_success.html",
        {
            "order": order
        }
    )

@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by("-created_at")

    return render(request, "orders/order_history.html", {
        "orders": orders
    })


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(
        Order.objects.select_related("address").prefetch_related("items__product"),
        id=order_id,
        user=request.user,
    )

    return render(request, "orders/order_detail.html", {
        "order": order,
    })

@login_required
@require_POST
def cancel_order(request, order_id):

    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    if order.status in ["pending", "confirmed"]:
        order.status = "cancelled"
        order.cancelled_at = timezone.now()
        order.payment_status = False
        order.save()

        order.items.all().update(status="cancelled")

        messages.success(request, "Your order has been cancelled successfully.")

    else:
        messages.error(request, "This order cannot be cancelled.")

    return redirect("orders:order_detail", order_id=order.id)


@login_required
@require_POST
def delete_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if order.status in ["cancelled", "delivered"]:
        order.delete()
        messages.success(request, "Order history removed successfully.")
    else:
        messages.error(request, "Active orders cannot be deleted.")

    return redirect("orders:my_orders")


@login_required
@require_POST
def update_order_status(request, item_id):
    item = get_object_or_404(OrderItem, id=item_id)
    order = item.order

    if order.status == "cancelled":
        messages.error(request, "This order is cancelled and its status cannot be changed.")
        return redirect("seller_dashboard")
    
    if hasattr(item.product, 'seller') and item.product.seller and item.product.seller != request.user and not request.user.is_superuser:
        messages.error(request, "You do not have permission to update this order status.")
        return redirect("seller_dashboard")

    new_status = request.POST.get("status", "").strip().lower()
    valid_statuses = [choice[0] for choice in OrderItem.STATUS_CHOICES]

    if new_status in valid_statuses:
        item.status = new_status
        item.save()

        order.update_status_from_items()

        messages.success(request, f"Order #{order.id} item status updated to {new_status.capitalize()}.")
    else:
        messages.error(request, "Invalid status selected.")

    return redirect("seller_dashboard")


@login_required
def seller_orders(request):
    if request.user.is_superuser:
        order_items = OrderItem.objects.all().select_related("order", "product", "order__user", "order__address").order_by("-order__created_at")
    else:
        order_items = OrderItem.objects.filter(product__seller=request.user).select_related("order", "product", "order__user", "order__address").order_by("-order__created_at")

    status_filter = request.GET.get("status")
    search_query = request.GET.get("q")

    if status_filter:
        order_items = order_items.filter(status=status_filter)
    
    if search_query:
        order_items = order_items.filter(product__name__icontains=search_query)

    return render(request, "seller/seller_orders.html", {
        "order_items": order_items,
        "status_filter": status_filter,
        "search_query": search_query,
    })


@login_required
def seller_coupons(request):
    coupons = Coupon.objects.all().order_by("-created_at")
    return render(request, "seller/seller_coupons.html", {"coupons": coupons})


@login_required
def add_coupon(request):
    if request.method == "POST":
        code = request.POST.get("code")
        discount_type = request.POST.get("discount_type")
        discount_value = request.POST.get("discount_value")
        minimum_order_amount = request.POST.get("minimum_order_amount", 0)
        valid_from = request.POST.get("valid_from")
        valid_until = request.POST.get("valid_until")
        usage_limit = request.POST.get("usage_limit")

        try:
            Coupon.objects.create(
                code=code,
                discount_type=discount_type,
                discount_value=discount_value,
                minimum_order_amount=minimum_order_amount,
                valid_from=parse_datetime(valid_from),
                valid_until=parse_datetime(valid_until),
                usage_limit=usage_limit if usage_limit else None,
            )
            messages.success(request, "Coupon created successfully.")
            return redirect("orders:seller_coupons")
        except Exception as e:
            messages.error(request, f"Error creating coupon: {str(e)}")

    return render(request, "seller/add_coupon.html")


@login_required
@require_POST
def toggle_coupon(request, coupon_id):
    coupon = get_object_or_404(Coupon, id=coupon_id)
    coupon.is_active = not coupon.is_active
    coupon.save()
    messages.success(request, f"Coupon {coupon.code} status updated.")
    return redirect("orders:seller_coupons")


@login_required
def seller_earnings(request):
    if request.user.is_superuser:
        order_items = OrderItem.objects.all().select_related("order", "product")
    else:
        order_items = OrderItem.objects.filter(product__seller=request.user).select_related("order", "product")

    total_earnings = sum(item.total_price for item in order_items if item.status == "delivered")
    pending_earnings = sum(item.total_price for item in order_items if item.status in ["pending", "confirmed", "shipped"])
    net_earnings = total_earnings

    return render(request, "seller/seller_earnings.html", {
        "order_items": order_items,
        "total_earnings": total_earnings,
        "pending_earnings": pending_earnings,
        "net_earnings": net_earnings,
    })


@login_required
def export_sales_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="sales_report.csv"'

    writer = csv.writer(response)
    writer.writerow(['Order ID', 'Product', 'Quantity', 'Selling Price', 'Total Price', 'Status', 'Date'])

    if request.user.is_superuser:
        order_items = OrderItem.objects.all().select_related("order", "product").order_by("-order__created_at")
    else:
        order_items = OrderItem.objects.filter(product__seller=request.user).select_related("order", "product").order_by("-order__created_at")

    for item in order_items:
        writer.writerow([
            item.order.id,
            item.product.name,
            item.quantity,
            item.selling_price,
            item.total_price,
            item.status,
            item.order.created_at.strftime('%Y-%m-%d %H:%M')
        ])

    return response