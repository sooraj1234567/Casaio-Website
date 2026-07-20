from django import forms
from .models import Address


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = [
            "full_name",
            "phone_number",
            "house_name",
            "area",
            "city",
            "state",
            "pincode",
        ]

        widgets = {
            "full_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Full Name"
            }),

            "phone_number": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Phone Number"
            }),

            "house_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "House / Flat / Building"
            }),

            "area": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Area / Street"
            }),

            "city": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "City"
            }),

            "state": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "State"
            }),

            "pincode": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Pincode"
            }),
        }