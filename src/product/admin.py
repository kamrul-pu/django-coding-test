"""Add Product related models in admin panel."""
from django.contrib import admin

from product.models import (
    Variant,
    Product,
    ProductImage,
    ProductVariant,
    ProductVariantPrice,
)


class VariantAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "description",
        "active",
    )


admin.site.register(Variant, VariantAdmin)


class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "sku",
        "description",
    )


admin.site.register(Product, ProductAdmin)


class ProductImageAdmin(admin.ModelAdmin):
    list_display = ("file_path",)


admin.site.register(ProductImage, ProductImageAdmin)


class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ("pk", "variant_title")


admin.site.register(ProductVariant, ProductVariantAdmin)


class ProductVariantPriceAdmin(admin.ModelAdmin):
    list_display = (
        "price",
        "stock",
    )


admin.site.register(ProductVariantPrice, ProductVariantPriceAdmin)
