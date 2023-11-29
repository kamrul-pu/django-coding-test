from django.core.paginator import Paginator
from django.http import JsonResponse
import json
from django.views import generic

from product.forms import ProductForm, ProductVariantPriceForm
from product.models import (
    Variant,
    Product,
    ProductImage,
    ProductVariant,
    ProductVariantPrice,
)


class CreateProductView(generic.TemplateView):
    template_name = "products/create.html"

    def get_context_data(self, **kwargs):
        # Get context data for rendering the template
        context = super(CreateProductView, self).get_context_data(**kwargs)

        # Fetch active variants and add them to the context
        variants = Variant.objects.filter(active=True).values("id", "title")
        context["product"] = True
        context["variants"] = list(variants.all())

        return context

    def post(self, request, *args, **kwargs):
        # Handle product creation here based on JSON data
        data = request.POST

        # Extract product details from the request data
        product_name = data.get("product_name", "")
        product_sku = data.get("product_sku", "")
        description = data.get("description", "")
        # Add more fields as needed...

        # Create the main product object
        product = Product.objects.create(
            title=product_name,
            sku=product_sku,
            description=description
            # Add more fields as needed...
        )

        # Extract product variants from the request data
        variants = data.get("product_variants", [])
        variants_json = json.loads(variants)

        # Handle product variants
        product_variants = []
        for variant in variants_json:
            product_variants.append(
                ProductVariant(
                    variant_title=variant["tags"],
                    variant_id=variant["option"],
                    product_id=product.id,
                )
            )

        # Bulk create product variants
        if product_variants:
            ProductVariant.objects.bulk_create(product_variants)

        # Return a JSON response indicating success
        return JsonResponse({"success": True})


class ProductListView(generic.ListView):
    model = Product
    template_name = "products/list.html"
    context_object_name = "products"
    paginate_by = 5

    def get_queryset(self):
        # get the filters from the GET request
        title = self.request.GET.get("title", None)
        variant = self.request.GET.get("variant", None)
        price_from = self.request.GET.get("price_from", None)
        price_to = self.request.GET.get("price_to", None)
        date = self.request.GET.get("date", None)
        queryset = Product.objects.filter().prefetch_related(
            "productvariant_set", "productvariantprice_set"
        )
        # filter based on provided field
        if title:
            queryset = queryset.filter(title__icontains=title)
        if variant:
            queryset = queryset.filter(productvariant__variant_id=variant)
        if price_from and price_to:
            queryset = queryset.filter(
                productvariantprice__price__range=[price_from, price_to]
            )
        if date:
            queryset = queryset.filter(created_at__date=date)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        variants = Variant.objects.filter(active=True).values("id", "title")
        products = list(self.get_queryset())
        paginator = Paginator(products, self.paginate_by)

        page = self.request.GET.get("page")
        context["products"] = paginator.get_page(page)
        context["variants"] = variants

        return context


class ProductUpdateView(generic.UpdateView):
    model = Product
    form_class = ProductForm
    template_name = "products/update.html"
    success_url = "/product/list"

    def get_context_data(self, **kwargs):
        # Retrieve the current product and its associated variant prices
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        variant_prices = ProductVariantPrice.objects.filter(product=product)

        # Create forms for the product and its variant prices
        context["variant_forms"] = [
            ProductVariantPriceForm(instance=variant) for variant in variant_prices
        ]
        context["product_form"] = ProductForm(instance=product)
        return context

    def form_valid(self, form):
        # Validate the main product form and all variant price forms
        product_form = ProductForm(self.request.POST, instance=self.get_object())
        variant_forms = [
            ProductVariantPriceForm(self.request.POST, instance=variant)
            for variant in self.get_object().productvariantprice_set.all()
        ]

        # Check if all forms are valid before saving data
        if all(
            [product_form.is_valid(), form.is_valid()]
            + [vf.is_valid() for vf in variant_forms]
        ):
            # Save the main product form
            product_form.save()

            # Save the main form (assumes it's associated with the main product)
            form.save()

            # Save each variant price form
            for vf in variant_forms:
                vf.save()

            # Continue with the default behavior for a valid form
            return super().form_valid(form)

        # Handle the case where one or more forms are invalid
        return self.form_invalid(form)
