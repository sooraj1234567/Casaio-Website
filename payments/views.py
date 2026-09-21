import json
import razorpay
import logging
from django.http import JsonResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.db import transaction
from orders.models import Order
from cart.models import Cart
from notifications.services import send_email_notification, send_order_whatsapp_notification

logger = logging.getLogger(__name__)

client = razorpay.Client(
    auth=(
        settings.RAZORPAY_KEY_ID,
        settings.RAZORPAY_KEY_SECRET,
    )
)

@login_required
@require_http_methods(["POST"])
@transaction.atomic
def verify_payment(request):
    """Verify Razorpay payment signature and update order status"""

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        logger.error("Invalid JSON in payment verification request")
        return JsonResponse({
            "success": False,
            "message": "Invalid request format"
        }, status=400)

    # Validate required fields
    required_fields = ["order_id", "razorpay_order_id", "razorpay_payment_id", "razorpay_signature"]
    if not all(field in data for field in required_fields):
        logger.error("Missing required fields in payment verification")
        return JsonResponse({
            "success": False,
            "message": "Missing required fields"
        }, status=400)

    try:
        order = Order.objects.select_for_update().get(
            id=data["order_id"],
            user=request.user,
        )
    except Order.DoesNotExist:
        logger.error(f"Order not found: {data['order_id']}")
        return JsonResponse({
            "success": False,
            "message": "Order not found"
        }, status=404)

    if order.payment_method != "razorpay":
        return JsonResponse({
            "success": False,
            "message": "This order does not use Razorpay"
        }, status=400)

    if order.razorpay_order_id != data["razorpay_order_id"]:
        return JsonResponse({
            "success": False,
            "message": "Payment order does not match this order"
        }, status=400)

    if order.payment_status:
        return JsonResponse({
            "success": True,
            "redirect_url": f"/orders/success/{order.id}/"
        })

    try:
        # Verify payment signature
        client.utility.verify_payment_signature({
            "razorpay_order_id": data["razorpay_order_id"],
            "razorpay_payment_id": data["razorpay_payment_id"],
            "razorpay_signature": data["razorpay_signature"]
        })

        # Payment verified successfully
        order.payment_status = True
        order.status = "confirmed"
        order.razorpay_payment_id = data["razorpay_payment_id"]
        order.razorpay_signature = data["razorpay_signature"]
        order.save()

        # Clear cart
        cart = Cart.objects.filter(user=order.user).first()
        if cart:
            cart.items.all().delete()

        send_email_notification(
            subject="Order confirmed",
            recipient=order.user.email,
            message=(
                f"Hello {order.user.username},\n\n"
                f"Your order {order.order_number or order.id} has been confirmed and payment was successful.\n"
                "We will keep you updated as your order is processed."
            ),
        )

        phone_number = getattr(order.user, "phone_number", "") or getattr(order.address, "phone_number", "")
        if phone_number:
            send_order_whatsapp_notification(
                phone_number=phone_number,
                order_number=order.order_number or str(order.id),
                template_name="order_confirmed",
                amount=f"₹{order.total}",
            )

        logger.info(f"Payment verified successfully for order {order.id}")

        return JsonResponse({
            "success": True,
            "redirect_url": f"/orders/success/{order.id}/"
        })

    except razorpay.errors.SignatureVerificationError as e:
        logger.error(f"Razorpay signature verification failed: {str(e)}")
        return JsonResponse({
            "success": False,
            "message": "Payment verification failed"
        }, status=400)

    except Exception as e:
        logger.error(f"Unexpected error in payment verification: {str(e)}")
        return JsonResponse({
            "success": False,
            "message": "An unexpected error occurred"
        }, status=500)