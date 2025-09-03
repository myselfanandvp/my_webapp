from products.filters import ProductFilter
import django_filters
from products.models import ProductColor
from django import forms

class Myfilter(ProductFilter):
    search = django_filters.CharFilter(
        field_name='name',
        lookup_expr='icontains',
        label='Search',
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Search products...',
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'
            }
        )
    )
    order = django_filters.OrderingFilter(
        fields=(
            ('name', 'name'),
            ('category', 'category'),
            ('price', 'price')
        ),
        field_labels={
            'name': 'name',
            'category': 'category',
            'price': 'price',
        },
        choices=[
            ('name', 'Product Name (A–Z)'),
            ('-name', 'Product Name (Z–A)'),
            ('category', 'Category(A-Z)'),
            ('-category', 'Category(Z-A)'),
            ('price', 'Price: Low to High'),
            ('-price', "Price: High to Low"),
        ],
        label='Sort By',
        empty_label="Relevance",
        widget=forms.Select
        
        )

    colors = django_filters.ModelMultipleChoiceFilter(
        queryset=ProductColor.objects.all(),
        label="Colors",

        widget=forms.SelectMultiple(  # or use SelectMultiple if you prefer a dropdown
            attrs={
                'class': 'fbg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'
            }
        )
    )

       
    class Meta(ProductFilter.Meta):
        fields = ProductFilter.Meta.fields.copy()
     
