from django.urls import path
from . import views

app_name = "cart"

urlpatterns = [
    path("", views.cart_page, name="cart_page"),
    path("data/", views.get_cart_data, name="cart_data"),
    path("add/<int:product_id>/", views.add_to_cart, name="add_cart"),
    path("buy-now/<int:product_id>/", views.buy_now, name="buy_now"),
    path("remove/<int:item_id>/", views.remove_from_cart, name="remove_from_cart"),
    path("update/<int:item_id>/", views.update_cart_quantity, name="update_cart_quantity"),
]