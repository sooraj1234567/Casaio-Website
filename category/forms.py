from django import forms
from .models import Category
from .utils import get_category_choices


class CategoryForm(forms.ModelForm):

    parent = forms.ModelChoiceField(
        queryset=Category.objects.none(),
        required=False,
        empty_label="No Parent Category"
    )

    class Meta:
        model = Category

        fields = [
            "name",
            "parent",
            "description",
            "image",
            "is_active",
        ]

        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter category name"
            }),

            "parent": forms.Select(attrs={
                "class": "form-control"
            }),

            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 5,
                "placeholder": "Category description"
            }),

            "image": forms.ClearableFileInput(attrs={
                "class": "form-control"
            }),

            "is_active": forms.CheckboxInput(attrs={
                "class": "form-check-input"
            }),
        }