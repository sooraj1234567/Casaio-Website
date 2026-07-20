from django.urls import path
from . import views

app_name = "checkout"

urlpatterns = [
    path("", views.checkout_page, name="checkout"),
    path("save-address/", views.save_address, name="save_address"),
    path("delete-address/<int:address_id>/", views.delete_address, name="delete_address"),
    path("edit-address/<int:address_id>/", views.edit_address, name="edit_address"),
    path("set-default/<int:address_id>/", views.set_default_address, name="set_default_address"),
]