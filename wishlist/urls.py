from django.urls import path
from . import views

app_name = "wishlist"

urlpatterns = [
    path("", views.wishlist, name="wishlist"),
    path("toggle/<int:product_id>/", views.toggle_wishlist, name="toggle"),
    path("move_to_cart/<int:product_id>/", views.move_to_cart, name="move_to_cart"),
]