from django import forms

from .models import SellerPayoutProfile


class SellerPayoutProfileForm(forms.ModelForm):
    class Meta:
        model = SellerPayoutProfile
        fields = [
            "account_holder_name",
            "bank_name",
            "account_number",
            "ifsc_code",
            "upi_id",
        ]
        widgets = {
            "account_holder_name": forms.TextInput(attrs={"class": "form-control"}),
            "bank_name": forms.TextInput(attrs={"class": "form-control"}),
            "account_number": forms.TextInput(
                attrs={"class": "form-control", "inputmode": "numeric"}
            ),
            "ifsc_code": forms.TextInput(
                attrs={"class": "form-control", "maxlength": 11}
            ),
            "upi_id": forms.TextInput(attrs={"class": "form-control"}),
        }

    def clean_account_number(self):
        account_number = self.cleaned_data["account_number"].replace(" ", "")
        if not account_number.isdigit() or not 8 <= len(account_number) <= 34:
            raise forms.ValidationError(
                "Enter a valid bank account number between 8 and 34 digits."
            )
        return account_number

    def clean_ifsc_code(self):
        ifsc_code = self.cleaned_data["ifsc_code"].strip().upper()
        if len(ifsc_code) != 11 or ifsc_code[4] != "0":
            raise forms.ValidationError("Enter a valid 11-character IFSC code.")
        return ifsc_code
