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

    path(
        "<int:order_id>/delete/",
        views.delete_order,
        name="delete_order"
    ),

    path(
        "seller/orders/",
        views.seller_orders,
        name="seller_orders"
    ),

    path(
        "seller/orders/update/<int:item_id>/",
        views.update_order_status,
        name="update_order_status"
    ),

    path(
        "seller/coupons/",
        views.seller_coupons,
        name="seller_coupons"
    ),

    path(
        "seller/coupons/add/",
        views.add_coupon,
        name="add_coupon"
    ),

    path(
        "seller/coupons/toggle/<int:coupon_id>/",
        views.toggle_coupon,
        name="toggle_coupon"
    ),

    path(
        "seller/earnings/",
        views.seller_earnings,
        name="seller_earnings"
    ),

    path(
        "seller/earnings/export/",
        views.export_sales_csv,
        name="export_sales_csv"
    ),
]