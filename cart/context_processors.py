from .models import Cart, CartItem

def cart_count(request):

    count = 0

    if request.user.is_authenticated:

        cart = Cart.objects.filter(user=request.user).first()

        if cart:
            count = CartItem.objects.filter(cart=cart).count()

    return {
        "cart_count": count
    }