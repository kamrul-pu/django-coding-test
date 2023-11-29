from django.core.paginator import Paginator
from django.views import generic

from product.models import Variant, Product


class CreateProductView(generic.TemplateView):
    template_name = "products/create.html"

    def get_context_data(self, **kwargs):
        context = super(CreateProductView, self).get_context_data(**kwargs)
        variants = Variant.objects.filter(active=True).values("id", "title")
        context["product"] = True
        context["variants"] = list(variants.all())
        return context


class ProductListView(generic.ListView):
    model = Product
    template_name = "products/list.html"
    context_object_name = "products"
    paginate_by = 2

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
