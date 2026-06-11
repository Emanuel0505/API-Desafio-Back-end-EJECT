import django_filters
from .models import Product

class Product_Filter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr='lte')

    title = django_filters.CharFilter(lookup_expr='icontains')

    color = django_filters.CharFilter(field_name='stock__color_name', lookup_expr='iexact')
    size = django_filters.CharFilter(field_name='stock__size', lookup_expr='iexact')

    class Meta:
        model = Product
        fields = [
            'category',
            'min_price',
            'max_price',
            'title',
            'color',
            'size',
        ]