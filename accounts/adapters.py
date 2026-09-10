from allauth.account.adapter import DefaultAccountAdapter


class CasaioAccountAdapter(DefaultAccountAdapter):

    def get_login_redirect_url(self, request):
        user = request.user

        if getattr(user, "role", None) == "seller":
            return "/seller/dashboard/"

        if getattr(user, "role", None) == "admin":
            return "/dashboard/"

        return "/"