import random
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import user_passes_test
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render

from category.models import Category
from accounts.models import SellerApplication
from product.models import Product
from orders.models import OrderItem

User = get_user_model()

otp_storage = {}


def seller_required(function):
    return user_passes_test(
        lambda u: u.is_authenticated and getattr(u, "role", None) == "seller",
        login_url="/login/",
    )(function)


def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        role = request.POST.get("role", "customer")

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
            "password": password,
            "role": role,
        }

        request.session["email"] = email

        send_mail(
            subject="Casaio Email Verification",
            message=(
                f"Your Casaio verification OTP is: {otp}\n\nThis OTP is valid for 10"
                " minutes."
            ),
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=False,
        )

        messages.success(request, "OTP sent to your email.")
        return redirect("verify_otp")

    return render(request, "account/register.html")

def seller_register(request):
    categories = Category.objects.all()

    if request.method == "POST":
        full_name = request.POST.get("full_name")
        username = request.POST.get("username")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        business_name = request.POST.get("business_name")
        business_category = request.POST.get("business_category")

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("seller_register")

        # Check whether the email already belongs to an existing account
        existing_user = User.objects.filter(email=email).first()

        if existing_user:
            # Existing customer can use the same account
            if existing_user.role == "seller":
                messages.error(
                    request,
                    "You already have a seller account with this email."
                )
                return redirect("seller_register")

            if existing_user.role == "admin":
                messages.error(
                    request,
                    "This email belongs to an admin account."
                )
                return redirect("seller_register")

            # Existing customer
            if existing_user.username != username:
                messages.error(
                    request,
                    "This email is already registered. Please use your existing username."
                )
                return redirect("seller_register")

            # Store seller application information temporarily
            otp = str(random.randint(100000, 999999))

            otp_storage[email] = {
                "otp": otp,
                "user_id": existing_user.id,
                "full_name": full_name,
                "username": existing_user.username,
                "phone": phone,
                "business_name": business_name,
                "business_category": business_category,
                "role": "seller",
                "existing_user": True,
            }

        else:
            # New user applying directly as a seller
            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already exists")
                return redirect("seller_register")

            otp = str(random.randint(100000, 999999))

            otp_storage[email] = {
                "otp": otp,
                "full_name": full_name,
                "username": username,
                "password": password,
                "phone": phone,
                "business_name": business_name,
                "business_category": business_category,
                "role": "seller",
                "existing_user": False,
            }

        request.session["email"] = email

        send_mail(
            subject="Casaio Seller Verification",
            message=(
                f"Your Casaio seller verification OTP is: {otp}\n\n"
                "This OTP is valid for 10 minutes."
            ),
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=False,
        )

        messages.success(request, "OTP sent to your email.")
        return redirect("verify_otp")

    return render(
        request,
        "account/seller_register.html",
        {"categories": categories}
    )

def verify_otp(request):
    if request.method == "POST":
        email = request.session.get("email")
        entered_otp = request.POST.get("otp")

        if email in otp_storage and otp_storage[email]["otp"] == entered_otp:
            data = otp_storage[email]

            # Safely fetch the Category instance
            category_instance = None
            cat_val = data.get("business_category")

            if cat_val:
                try:
                    category_instance = Category.objects.get(id=cat_val)
                except (Category.DoesNotExist, ValueError, TypeError):
                    category_instance = Category.objects.filter(
                        name=cat_val
                    ).first()

            # -------------------------------------------------
            # EXISTING CUSTOMER → SELLER APPLICATION
            # -------------------------------------------------
            if data.get("existing_user"):
                user = User.objects.get(id=data["user_id"])

                # Update seller-related information
                user.first_name = data.get("full_name", "")
                user.phone_number = data.get("phone", "")
                user.business_name = data.get("business_name", "")
                user.business_category = category_instance

                # Keep role as customer until admin approves
                user.save()

                # Create a SellerApplication instance
                SellerApplication.objects.update_or_create(
                    user=user,
                    defaults={
                        "business_name": data.get("business_name", ""),
                        "business_category": category_instance,
                        "status": "pending",    
                    },
                )

                del otp_storage[email]
                request.session.pop("email", None)

                messages.success(
                    request,
                    "Seller application submitted successfully. "
                    "Your application is now pending admin approval."
                )

                return redirect("login")

            # -------------------------------------------------
            # NEW SELLER → CREATE NEW ACCOUNT
            # -------------------------------------------------
            user = User.objects.create_user(
                username=data["username"],
                email=email,
                password=data["password"],
                role=data.get("role", "customer"),
                first_name=data.get("full_name", ""),
                phone_number=data.get("phone", ""),
                business_name=data.get("business_name", ""),
                business_category=category_instance,
            )

            del otp_storage[email]
            request.session.pop("email", None)

            messages.success(
                request,
                "Account created successfully."
            )

            return redirect("login")

        else:
            messages.error(request, "Invalid OTP")

    return render(request, "account/verify_otp.html")


def user_login(request):
    if request.method == "POST":
        login_input = request.POST.get("username") or request.POST.get("email")
        password = request.POST.get("password")

        user = None

        if login_input:
            if "@" in login_input:
                try:
                    matched_user = User.objects.get(email=login_input)
                    user = authenticate(
                        request,
                        username=matched_user.username,
                        password=password
                    )
                except User.DoesNotExist:
                    user = None
            else:
                user = authenticate(
                    request,
                    username=login_input,
                    password=password
                )

        if user:
            # ==========================================
            # ADMIN LOGIN
            # Admin does NOT require OTP
            # ==========================================
            if getattr(user, "role", None) == "admin":
                login(
                    request,
                    user,
                    backend="django.contrib.auth.backends.ModelBackend"
                )

                messages.success(request, "Admin login successful.")

                return redirect("dashboard:dashboard")

            # ==========================================
            # SELLER / CUSTOMER LOGIN
            # OTP REQUIRED
            # ==========================================
            otp = str(random.randint(100000, 999999))

            otp_storage[user.email] = {
                "otp": otp,
                "user_id": user.id,
                "purpose": "login",
            }

            request.session["login_email"] = user.email

            send_mail(
                subject="Casaio Login OTP",
                message=f"Your Casaio login OTP is: {otp}",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user.email],
                fail_silently=False,
            )

            messages.success(request, "OTP sent to your email.")

            return redirect("login_otp")

        else:
            messages.error(request, "Invalid username or password")

    return render(request, "account/login.html")


def login_otp(request):
    if request.method == "POST":
        entered_otp = request.POST.get("otp")
        email = request.session.get("login_email")

        if email in otp_storage:
            data = otp_storage[email]

            if (
                data.get("otp") == entered_otp
                and data.get("purpose") == "login"
            ):
                user = User.objects.get(id=data["user_id"])

                login(
                    request,
                    user,
                    backend="django.contrib.auth.backends.ModelBackend",
                )

                del otp_storage[email]
                request.session.pop("login_email", None)

                messages.success(request, "Login Successful")

                # Seller → Seller Dashboard
                if getattr(user, "role", None) == "seller":
                    return redirect("seller_dashboard")

                # Customer → Home
                return redirect("home")

            else:
                messages.error(request, "Invalid OTP")

        else:
            messages.error(request, "OTP expired or invalid. Please login again.")

    return render(request, "account/login_otp.html")


def user_logout(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect("login")


def home(request):
    categories = Category.objects.all()
    context = {
        "categories": categories,
    }
    return render(request, "home/home.html", context)


def category_products(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    products = Product.objects.filter(category=category)
    categories = Category.objects.all()
    context = {
        'category': category,
        'products': products,
        'categories': categories,
    }
    return render(request, 'category/category_detail.html', context)


def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email")

        try:
            user = User.objects.get(email=email)

            otp = str(random.randint(100000, 999999))

            otp_storage[email] = {
                "otp": otp,
                "user_id": user.id,
                "purpose": "forgot_password",
            }

            request.session["reset_email"] = email

            send_mail(
                subject="Casaio Password Reset OTP",
                message=f"Your OTP is: {otp}",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
                fail_silently=False,
            )

            messages.success(request, "OTP sent successfully.")

            return redirect("forgot_password_otp")

        except User.DoesNotExist:
            messages.error(request, "Email not registered.")

    return render(request, "account/forgot_password.html")


def forgot_password_otp(request):
    if request.method == "POST":
        entered_otp = request.POST.get("otp")
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
        password = request.POST.get("password")
        confirm = request.POST.get("confirm_password")

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


# --- Seller Dashboard Views ---


@seller_required
def seller_dashboard(request):
    products = Product.objects.filter(seller=request.user)
    order_items = OrderItem.objects.filter(product__seller=request.user)

    context = {
        "products": products,
        "order_items": order_items,
        "total_products": products.count(),
        "total_orders": order_items.count(),
    }
    return render(request, "seller/dashboard.html", context)


@seller_required
def seller_products(request):
    products = Product.objects.filter(seller=request.user)
    return render(request, 'seller/seller_products.html', {'products': products})


@seller_required
def add_product(request):
    categories = Category.objects.all()
    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")
        selling_price = request.POST.get("selling_price") or request.POST.get("price")
        supplier_price = request.POST.get("supplier_price") or selling_price
        stock = request.POST.get("stock")
        category_id = request.POST.get("category")
        image = request.FILES.get("image")

        category = (
            get_object_or_404(Category, id=category_id) if category_id else None
        )

        Product.objects.create(
            seller=request.user,
            name=name,
            description=description,
            selling_price=selling_price,
            supplier_price=supplier_price,
            stock=stock,
            category=category,
            image=image,
        )
        messages.success(request, "Product added successfully!")
        return redirect("seller_dashboard")

    return render(request, "seller/add_product.html", {"categories": categories})


@seller_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, seller=request.user)
    categories = Category.objects.all()
    if request.method == 'POST':
        product.name = request.POST.get('name')
        product.description = request.POST.get('description')
        product.selling_price = request.POST.get('selling_price') or request.POST.get('price')
        product.supplier_price = request.POST.get('supplier_price') or product.selling_price
        product.stock = request.POST.get('stock')
        category_id = request.POST.get('category')
        product.category = get_object_or_404(Category, id=category_id) if category_id else None
        
        if 'image' in request.FILES:
            product.image = request.FILES['image']
            
        product.save()
        messages.success(request, "Product updated successfully!")
        return redirect('seller_products')

    return render(request, 'seller/edit_product.html', {'product': product, 'categories': categories})


@seller_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, seller=request.user)
    if request.method == 'POST':
        product.delete()
        messages.success(request, "Product deleted successfully!")
        return redirect('seller_products')
    return render(request, 'seller/delete_product.html', {'product': product})


@seller_required
def update_order_status(request, item_id):
    order_item = get_object_or_404(OrderItem, id=item_id, product__seller=request.user)
    if request.method == "POST":
        new_status = request.POST.get("status")
        order_item.status = new_status
        order_item.save()
        messages.success(request, "Order status updated successfully!")
    return redirect("seller_dashboard")