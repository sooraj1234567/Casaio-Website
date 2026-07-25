from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import transaction

from cart.models import Cart
from checkout.models import Address

from .models import Order, OrderItem

import razorpay
from django.conf import settings
import logging

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
        subtotal += item.product.price * item.quantity

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
            price=item.product.price,
        )

    if payment_method == "cod":

        order.payment_status = True
        order.status = "confirmed"
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