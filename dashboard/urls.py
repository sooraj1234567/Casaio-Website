from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [

    path(
        "",
        views.dashboard,
        name="dashboard"
    ),

    path(
        "orders/",
        views.order_list,
        name="order_list"
    ),

    path(
        'orders/<int:pk>/',
        views.order_detail,
        name='order_detail'
    ),

    path(
        "orders/<int:pk>/update-status/",
        views.update_order_status,
        name="update_order_status"
    ),

    path(
        "products/",
        views.product_list,
        name="product_list"
    ),

    path(
        "products/add/",
        views.product_create,
        name="product_create",
    ),

    path(
        "products/<int:pk>/edit/",
        views.product_update,
        name="product_update",
    ),

    path(
        "products/<int:pk>/delete/",
        views.delete_gallery_image,
        name="delete_gallery_image",
    ),

    path(
        "products/<int:pk>/delete/",
        views.product_delete,
        name="product_delete",
    ),

    path(
        "categories/",
        views.category_list,
        name="category_list"
    ),

    path(
        "categories/add/",
        views.category_create,
        name="category_create",
    ),

    path(
    "categories/<int:pk>/edit/",
    views.category_update,
    name="category_update",
),

path(
    "categories/delete/<int:pk>/",
    views.category_delete,
    name="category_delete",
),

]