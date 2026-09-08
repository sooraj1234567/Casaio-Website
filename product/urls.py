from django.urls import path
from . import views

urlpatterns = [
    path(
        "products/",
        views.product_list,
        name="product_list"
    ),
    path(
        "products/<slug:slug>/",
        views.product_detail,
        name="product_detail"
    ),
    path(
        "seller/dashboard/",
        views.seller_dashboard,
        name="seller_dashboard"
    ),
    path(
        "seller/inventory/",
        views.seller_inventory,
        name="seller_inventory"
    ),
    path(
        "seller/inventory/update/<int:product_id>/",
        views.update_stock,
        name="update_stock"
    ),
    path(
        "seller/product/edit/<int:product_id>/",
        views.edit_product,
        name="edit_product"
    ),
    path(
        "seller/product/delete/<int:product_id>/",
        views.delete_product,
        name="delete_product"
    ),
    path(
        "seller/reviews/",
        views.seller_reviews,
        name="seller_reviews"
    ),
]