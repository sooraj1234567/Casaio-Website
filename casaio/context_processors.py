AUTH_PAGE_NAMES = {
    "login",
    "register",
    "seller_register",
    "forgot_password",
    "verify_otp",
    "login_otp",
    "forgot_password_otp",
    "reset_password",
}


def store_chrome(request):
    url_name = getattr(getattr(request, "resolver_match", None), "url_name", None)
    return {
        "show_store_chrome": url_name not in AUTH_PAGE_NAMES,
    }
