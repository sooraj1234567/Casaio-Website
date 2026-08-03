from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect

from product.models import Product
from .forms import ReviewForm
from .models import Review


@login_required
def add_review(request, product_id):

    product = get_object_or_404(Product, id=product_id)

    review = Review.objects.filter(
        user=request.user,
        product=product
    ).first()

    if request.method == "POST":

        form = ReviewForm(
            request.POST,
            instance=review
        )

        if form.is_valid():

            review = form.save(commit=False)

            review.user = request.user
            review.product = product

            review.save()

            messages.success(
                request,
                "Review submitted successfully."
            )

    return redirect(
        "product:product_detail",
        slug=product.slug
    )