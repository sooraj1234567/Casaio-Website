from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.conf import settings
from .forms import AddressForm
from .models import Address
from django.shortcuts import get_object_or_404
from cart.models import Cart


@login_required
def saved_addresses(request):
    addresses = Address.objects.filter(user=request.user).order_by("-is_default", "-created_at")
    editing = get_object_or_404(addresses, id=request.GET.get("edit")) if request.GET.get("edit") else None

    if request.method == "POST":
        action = request.POST.get("action")
        if action in {"add", "edit"}:
            address_id = request.POST.get("address_id") if action == "edit" else None
            address = get_object_or_404(Address, id=address_id, user=request.user) if address_id else None
            form = AddressForm(request.POST, instance=address)
            if form.is_valid():
                saved = form.save(commit=False)
                saved.user = request.user
                if not addresses.exists():
                    saved.is_default = True
                saved.save()
                messages.success(request, "Address saved successfully.")
                return redirect("checkout:saved_addresses")
            editing = address
        elif action in {"default", "delete"}:
            address = get_object_or_404(Address, id=request.POST.get("address_id"), user=request.user)
            if action == "default":
                Address.objects.filter(user=request.user, is_default=True).update(is_default=False)
                address.is_default = True
                address.save(update_fields=["is_default"])
                messages.success(request, "Default address updated.")
            else:
                was_default = address.is_default
                address.delete()
                if was_default:
                    next_address = Address.objects.filter(user=request.user).first()
                    if next_address:
                        next_address.is_default = True
                        next_address.save(update_fields=["is_default"])
                messages.success(request, "Address removed.")
            return redirect("checkout:saved_addresses")
    else:
        form = AddressForm(instance=editing)

    return render(request, "checkout/saved_addresses.html", {
        "addresses": addresses,
        "form": form,
        "editing": editing,
    })

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
        "google_maps_api_key": settings.GOOGLE_MAPS_API_KEY,
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
