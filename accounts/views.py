from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

User = get_user_model()

import random
from django.core.mail import send_mail
from django.conf import settings

otp_storage = {}

def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect("register")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists")
            return redirect("register")

        otp = str(random.randint(100000, 999999))

        otp_storage[email] = {
            "otp": otp,
            "username": username,
            "password": password
        }

        request.session["email"] = email

        send_mail(
            subject="Casaio Email Verification",
            message=f"Your Casaio verification OTP is: {otp}\n\nThis OTP is valid for 10 minutes.",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=False,
        )

        messages.success(request, "OTP sent to your email.")
        return redirect("verify_otp")

    return render(request, "account/register.html")

def verify_otp(request):
    if request.method == "POST":
        email = request.session.get("email")
        entered_otp = request.POST["otp"]

        if email in otp_storage and otp_storage[email]["otp"] == entered_otp:
            data = otp_storage[email]

            user = User.objects.create_user(
                username=data["username"],
                email=email,
                password=data["password"]
            )

            del otp_storage[email]

            messages.success(request, "Account created successfully.")
            return redirect("login")

        else:
            messages.error(request, "Invalid OTP")

    return render(request, "account/verify_otp.html")

def user_login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Login successful")
            return redirect("/home")  # Redirect to a home page or dashboard
        else:
            messages.error(request, "Invalid username or password")

    return render(request, "account/login.html")


def user_logout(request):
    return render(request, "account/logout.html")