from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.user_login, name='login'),
    path('login-otp/', views.login_otp, name='login_otp'),
    path('register/', views.register, name='register'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('forgot_password_otp/', views.forgot_password_otp, name='forgot_password_otp'),
    path('reset-password/', views.reset_password, name='reset_password'),
    path('logout/', views.user_logout, name='logout'),
    
    # Category Products Endpoint
    path('category/<int:category_id>/', views.category_products, name='category_products'),
    
    # Seller Onboarding & Dashboard Endpoints
    path('seller/register/', views.seller_register, name='seller_register'),
    path('seller/dashboard/', views.seller_dashboard, name='seller_dashboard'),
    path('seller/products/', views.seller_products, name='seller_products'),
    path('seller/products/add/', views.add_product, name='add_product'),
    path('seller/products/edit/<int:product_id>/', views.edit_product, name='edit_product'),
    path('seller/products/delete/<int:product_id>/', views.delete_product, name='delete_product'),
    path('seller/order/update/<int:item_id>/', views.update_order_status, name='update_order_status'),
]