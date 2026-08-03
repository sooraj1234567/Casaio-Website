from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import JsonResponse
from .forms import AddressForm
from .models import Address
from django.shortcuts import get_object_or_404
from cart.models import Cart

@login_required
def checkout_page(request):

    form = AddressForm()

    addresses = Address.objects.filter(
        user=request.user
    ).order_by("-is_default", "-created_at")

    cart = Cart.objects.filter(user=request.user).first()

    subtotal = 0

    if cart:

        for item in cart.items.all():
            subtotal += item.product.selling_price * item.quantity

    context = {
        "form": form,
        "addresses": addresses,
        "cart": cart,
        "subtotal": subtotal,
        "total": subtotal,
    }

    return render(
        request,
        "checkout/checkout.html",
        context,
    )

@login_required
def save_address(request):

    if request.method == "POST":

        form = AddressForm(request.POST)

        if form.is_valid():

            address = form.save(commit=False)
            address.user = request.user

            # Make the first address the default
            if not request.user.addresses.exists():
                address.is_default = True

            address.save()

            return JsonResponse({
                "success": True,
                "message": "Address saved successfully!"
            })

        return JsonResponse({
            "success": False,
            "errors": form.errors
        })

    return JsonResponse({
        "success": False,
        "message": "Invalid request"
    })

@login_required
def delete_address(request, address_id):

    if request.method == "POST":

        address = get_object_or_404(
            Address,
            id=address_id,
            user=request.user
        )

        address.delete()

        return JsonResponse({
            "success": True
        })

    return JsonResponse({
        "success": False
    })

@login_required
def edit_address(request, address_id):

    address = get_object_or_404(
        Address,
        id=address_id,
        user=request.user
    )

    if request.method == "POST":

        form = AddressForm(request.POST, instance=address)

        if form.is_valid():

            form.save()

            return JsonResponse({
                "success": True
            })

        return JsonResponse({
            "success": False,
            "errors": form.errors
        })

    return JsonResponse({

        "id": address.id,
        "full_name": address.full_name,
        "phone_number": address.phone_number,
        "house_name": address.house_name,
        "area": address.area,
        "city": address.city,
        "state": address.state,
        "pincode": address.pincode,

    })

@login_required
def set_default_address(request, address_id):

    if request.method == "POST":

        # Remove old default
        Address.objects.filter(
            user=request.user,
            is_default=True
        ).update(is_default=False)

        # Set new default
        address = get_object_or_404(
            Address,
            id=address_id,
            user=request.user
        )

        address.is_default = True
        address.save()

        return JsonResponse({
            "success": True
        })

    return JsonResponse({
        "success": False
    })