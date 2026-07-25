import json
import razorpay
import logging
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from orders.models import Order
from cart.models import Cart

logger = logging.getLogger(__name__)

client = razorpay.Client(
    auth=(
        settings.RAZORPAY_KEY_ID,
        settings.RAZORPAY_KEY_SECRET,
    )
)

@csrf_exempt
@require_http_methods(["POST"])
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
        order = Order.objects.get(id=data["order_id"])
    except Order.DoesNotExist:
        logger.error(f"Order not found: {data['order_id']}")
        return JsonResponse({
            "success": False,
            "message": "Order not found"
        }, status=404)

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