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
    path('seller/payout-profile/', views.seller_payout_profile, name='seller_payout_profile'),
    path('seller/request-payout/', views.seller_request_payout, name='seller_request_payout'),
]