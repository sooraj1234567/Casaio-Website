from django.contrib.auth.decorators import user_passes_test


def seller_required(function):
    return user_passes_test(
        lambda user: user.is_authenticated
        and (getattr(user, "role", None) == "seller" or user.is_superuser),
        login_url="/login/",
    )(function)


def admin_required(function):
    return user_passes_test(
        lambda user: user.is_authenticated
        and (getattr(user, "role", None) == "admin" or user.is_superuser),
        login_url="/login/",
    )(function)
