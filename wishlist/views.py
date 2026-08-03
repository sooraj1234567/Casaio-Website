from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import Wishlist
from product.models import Product
from cart.models import Cart, CartItem


@login_required
def wishlist(request):

    wishlist_items = (
        Wishlist.objects
        .filter(user=request.user)
        .select_related("product")
        .order_by("-created_at")
    )

    return render(
        request,
        "wishlist/wishlist.html",
        {
            "wishlist_items": wishlist_items
        }
    )


@login_required
@require_POST
def toggle_wishlist(request, product_id):

    product = get_object_or_404(Product, id=product_id)

    wishlist_item = Wishlist.objects.filter(
        user=request.user,
        product=product
    )

    if wishlist_item.exists():

        wishlist_item.delete()

        return JsonResponse({
            "success": True,
            "action": "removed",
            "wishlist_count": Wishlist.objects.filter(
                user=request.user
            ).count()
        })

    Wishlist.objects.create(
        user=request.user,
        product=product
    )

    return JsonResponse({
        "success": True,
        "action": "added",
        "wishlist_count": Wishlist.objects.filter(
            user=request.user
        ).count()
    })


@login_required
@require_POST
def move_to_cart(request, product_id):

    product = get_object_or_404(Product, id=product_id)

    cart, created = Cart.objects.get_or_create(
        user=request.user
    )

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    Wishlist.objects.filter(
        user=request.user,
        product=product
    ).delete()

    wishlist_count = Wishlist.objects.filter(
        user=request.user
    ).count()

    cart_count = CartItem.objects.filter(
        cart=cart
    ).count()

    return JsonResponse({
        "success": True,
        "wishlist_count": wishlist_count,
        "cart_count": cart_count,
        "message": "Moved to cart successfully."
    })