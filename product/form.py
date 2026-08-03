from django import forms
from .models import Product
from category.models import Category
from category.utils import get_category_choices


class ProductForm(forms.ModelForm):

    category = forms.ModelChoiceField(
        queryset=Category.objects.none(),
        empty_label="Select Category"
    )

    class Meta:
        model = Product

        fields = [
            "category",
            "name",
            "description",
            "supplier_price",
            "selling_price",
            "is_offer_active",
            "offer_price",
            "stock",
            "image",
            "is_available",
        ]

        widgets = {

            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter product name"
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": "Enter product description"
                }
            ),

            "supplier_price": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "placeholder": "Supplier Price"
                }
            ),

            "selling_price": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "placeholder": "Selling Price"
                }
            ),

            "offer_price": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "placeholder": "Offer Price"
                }
            ),

            "stock": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Available Stock"
                }
            ),

            "category": forms.Select(
                attrs={
                    "class": "form-control"
                }
            ),

            "image": forms.ClearableFileInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "is_offer_active": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input"
                }
            ),

            "is_available": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input"
                }
            ),
        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        categories = get_category_choices()

        self.fields["category"].queryset = Category.objects.filter(
            id__in=[category.id for category in categories]
        )

        category_levels = {
            category.id: getattr(category, "level", 0)
            for category in categories
        }

        self.fields["category"].label_from_instance = (
            lambda obj: "{}{}".format(
                "— " * category_levels.get(obj.id, 0),
                obj.name,
            )
        )