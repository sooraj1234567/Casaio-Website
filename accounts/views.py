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

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user:

            otp = str(random.randint(100000,999999))

            otp_storage[user.email] = {
                "otp": otp,
                "user_id": user.id
            }

            request.session["login_email"] = user.email

            send_mail(
                subject="Casaio Login OTP",
                message=f"Your login OTP is: {otp}",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user.email],
                fail_silently=False,
            )

            messages.success(request,"OTP sent to your email.")

            return redirect("login_otp")

        else:

            messages.error(request,"Invalid username or password")

    return render(request,"account/login.html")

def login_otp(request):

    if request.method == "POST":

        entered_otp = request.POST["otp"]

        email = request.session.get("login_email")

        if email in otp_storage:

            if otp_storage[email]["otp"] == entered_otp:

                user = User.objects.get(
                    id=otp_storage[email]["user_id"]
                )

                login(request,user, backend="django.contrib.auth.backends.ModelBackend")

                del otp_storage[email]

                messages.success(request,"Login Successful")

                return redirect("home")

            else:

                messages.error(request,"Invalid OTP")

    return render(request,"account/login_otp.html")

def user_logout(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect("login")
    return render(request, "account/logout.html")

def home(request):
    return render(request, 'home/home.html')

def forgot_password(request):

    if request.method == "POST":

        email = request.POST["email"]

        try:

            user = User.objects.get(email=email)

            otp = str(random.randint(100000,999999))

            otp_storage[email] = {
                "otp": otp,
                "user_id": user.id,
                "purpose": "forgot_password"
            }

            request.session["reset_email"] = email

            send_mail(
                subject="Casaio Password Reset OTP",
                message=f"Your OTP is: {otp}",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
                fail_silently=False,
            )

            messages.success(request,"OTP sent successfully.")

            return redirect("forgot_password_otp")

        except User.DoesNotExist:

            messages.error(request,"Email not registered.")

    return render(request,"account/forgot_password.html")

def forgot_password_otp(request):

    if request.method == "POST":

        entered_otp = request.POST["otp"]
        email = request.session.get("reset_email")

        if email in otp_storage:

            if (
                otp_storage[email]["otp"] == entered_otp
                and otp_storage[email]["purpose"] == "forgot_password"
            ):

                return redirect("reset_password")

            else:
                messages.error(request, "Invalid OTP")

    return render(request, "account/forgot_password_otp.html")

def reset_password(request):

    email = request.session.get("reset_email")

    if not email:
        messages.error(request, "Session expired.")
        return redirect("forgot_password")

    if request.method == "POST":

        password = request.POST["password"]
        confirm = request.POST["confirm_password"]

        if password != confirm:
            messages.error(request, "Passwords do not match")
            return redirect("reset_password")

        user = User.objects.get(email=email)

        user.set_password(password)
        user.save()

        if email in otp_storage:
            del otp_storage[email]

        request.session.pop("reset_email", None)

        messages.success(request, "Password updated successfully")

        return redirect("login")

    return render(request, "account/reset_password.html")