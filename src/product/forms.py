from django.forms import (
    forms,
    ModelForm,
    CharField,
    TextInput,
    Textarea,
    BooleanField,
    CheckboxInput,
)

from product.models import (
    Product,
    ProductImage,
    ProductVariant,
    ProductVariantPrice,
    Variant,
)


class VariantForm(ModelForm):
    class Meta:
        model = Variant
        fields = "__all__"
        widgets = {
            "title": TextInput(attrs={"class": "form-control"}),
            "description": Textarea(attrs={"class": "form-control"}),
            "active": CheckboxInput(
                attrs={"class": "form-check-input", "id": "active"}
            ),
        }


class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = ["title", "sku", "description"]


class ProductVariantPriceForm(ModelForm):
    class Meta:
        model = ProductVariantPrice
        fields = ["price", "stock"]
