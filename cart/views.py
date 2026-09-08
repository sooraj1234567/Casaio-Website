from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import Cart, CartItem
from product.models import Product


@login_required
@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(
        Product,
        id=product_id
    )

    quantity = int(request.POST.get("quantity", 1))

    cart, created = Cart.objects.get_or_create(
        user=request.user
    )

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product
    )

    if created:
        cart_item.quantity = quantity
    else:
        if cart_item.quantity + quantity <= product.stock:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = product.stock

    cart_item.save()

    total_items = sum(
        item.quantity
        for item in cart.items.all()
    )

    return JsonResponse({
        "success": True,
        "message": "Product added to cart.",
        "product_name": product.name,
        "price": float(product.selling_price),
        "quantity": cart_item.quantity,
        "image": product.image.url if product.image else "",
        "total_items": total_items,
    })


@login_required
@require_POST
def buy_now(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get("quantity", 1))

    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if created:
        cart_item.quantity = quantity
    else:
        if cart_item.quantity + quantity <= product.stock:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = product.stock
    cart_item.save()

    return redirect("checkout:checkout_page")


@login_required
def get_cart_data(request):
    cart, created = Cart.objects.get_or_create(user=request.user)

    items = []
    subtotal = 0
    total_items = 0

    for item in cart.items.select_related("product"):
        total = item.product.selling_price * item.quantity

        subtotal += total
        total_items += item.quantity

        items.append({
            "id": item.id,
            "name": item.product.name,
            "price": float(item.product.selling_price),
            "quantity": item.quantity,
            "image": item.product.image.url if item.product.image else "",
        })

    return JsonResponse({
        "items": items,
        "subtotal": float(subtotal),
        "total_items": total_items,
    })


@login_required
@require_POST
def remove_from_cart(request, item_id):
    try:
        cart = Cart.objects.get(user=request.user)
        item = cart.items.get(id=item_id)

        item.delete()

        total_items = sum(item.quantity for item in cart.items.all())

        return JsonResponse({
            "success": True,
            "total_items": total_items,
        })

    except Cart.DoesNotExist:
        return JsonResponse({
            "success": False,
            "message": "Cart not found."
        }, status=404)

    except CartItem.DoesNotExist:
        return JsonResponse({
            "success": False,
            "message": "Item not found."
        }, status=404)


@login_required
@require_POST
def update_cart_quantity(request, item_id):
    action = request.POST.get("action")

    try:
        cart = Cart.objects.get(user=request.user)
        item = cart.items.get(id=item_id)

        if action == "increase":
            if item.quantity < item.product.stock:
                item.quantity += 1
                item.save()

        elif action == "decrease":
            if item.quantity > 1:
                item.quantity -= 1
                item.save()
            else:
                item.delete()

        total_items = sum(item.quantity for item in cart.items.all())

        return JsonResponse({
            "success": True,
            "total_items": total_items,
        })

    except Cart.DoesNotExist:
        return JsonResponse({
            "success": False,
            "message": "Cart not found."
        }, status=404)

    except CartItem.DoesNotExist:
        return JsonResponse({
            "success": False,
            "message": "Cart item not found."
        }, status=404)


@login_required
def cart_page(request):
    return render(request, "cart/cart.html")