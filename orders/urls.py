from django.urls import path
from . import views

app_name = "orders"

urlpatterns = [
    path(
        "place-order/",
        views.place_order,
        name="place_order"
    ),

    path(
        "success/<int:order_id>/",
        views.order_success,
        name="order_success"
    ),

    path(
        "my-orders/",
        views.my_orders,
        name="my_orders"
    ),

    path(
        "<int:order_id>/",
        views.order_detail,
        name="order_detail"
    ),

    path(
        "<int:order_id>/cancel/",
        views.cancel_order,
        name="cancel_order"
    ),
]