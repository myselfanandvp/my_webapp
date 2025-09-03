import django_filters
from .models import Product, ProductColor, Category, Brand
from django import forms



class ProductFilter(django_filters.FilterSet):
    is_deleted = django_filters.ChoiceFilter(
        label='Status',
        choices=[
            ('', 'All'),
            (0, 'Active'),
            (1, 'Not Active')
        ], empty_label=None,
        widget=forms.Select(
            attrs={
                'class': 'fg-gray-50 border border-gray-500 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'
            }
        )
    )
    name = django_filters.ModelChoiceFilter(
        queryset=Product.objects.all(),
        label='Product Name',
        empty_label="ALL",
        widget=forms.Select(
            attrs={
                'class': 'fg-gray-50 border border-gray-500 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'
            }
        )
    )
    colors = django_filters.ModelMultipleChoiceFilter(
    queryset=ProductColor.objects.all(),
    label="Colors",
    
    widget=forms.CheckboxSelectMultiple(  # or use SelectMultiple if you prefer a dropdown
        attrs={
            'class': 'flex justify-between items-center gap-2 bg-gray-200 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 '
        }
    )
)
    brand = django_filters.ModelChoiceFilter(
        queryset=Brand.objects.all(),
        label="Brand",
        empty_label="ALL",
        widget=forms.Select(
            attrs={
                'class': 'fg-gray-50 border border-gray-500 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'
            }
        )
    )

    category = django_filters.ModelChoiceFilter(
        queryset=Category.objects.all(),
        label="Category",
        empty_label="ALL",
        widget=forms.Select(
            attrs={
                'class': 'fg-gray-50 border border-gray-500 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'
            }
        )
    )
   

    class Meta:
       
        model = Product
        fields = ['name', 'category', 'brand', 'colors', 'is_deleted']


class CategoryFilter(django_filters.FilterSet):
    status = django_filters.ChoiceFilter(
        label='Status',
        choices=[
            ("", "All"),
            (1, "Active"),
            (0, "Inactive"),
        ],
        empty_label=None,
        widget=forms.Select(
            attrs={
                'class': 'fg-gray-50 border border-gray-500 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'
            }
        )
    )

    name = django_filters.ModelChoiceFilter(
        queryset=Category.objects.all(),
        label="Name",
        empty_label="All",

        widget=forms.Select(
            attrs={
                'class': 'fg-gray-50 border border-gray-500 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'
            }
        )

     )
    # slug = django_filters.CharFilter(field_name="slug", label="Slug",
    #                                  widget=forms.TextInput(
    #                                      attrs={
    #                                          'class': 'fg-gray-50 border border-gray-500 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'
    #                                      }
    #                                  )

    #                                  )

    # id = django_filters.CharFilter(lookup_expr="icontains", label='ID', widget=forms.TextInput(
    #     attrs={
    #         'class': 'fg-gray-50 border border-gray-500 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'

    #     }
    # ))
    
    order_by = django_filters.OrderingFilter(fields=(
        ('name', 'name'),
     
       
          
    ),field_labels={
            'name': 'Name',
         
           
          
        },
        choices=[
            ('name', 'Name  (Ascending)'),
            ('-name', 'Name  (Descending)'),
        
            
           
        ],
        label='Order By',
        empty_label="All",
      
        )
   

    class Meta:
        model = Category
        fields = [ 'status', 'name','order_by']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)  # initializes FilterSet properly
        
        
        for field in   self.form.fields.values():
           field.widget.attrs.update({
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': field.label, 
            })
           
           
           