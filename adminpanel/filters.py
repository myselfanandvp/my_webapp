import django_filters
from django.utils.timezone import timedelta
from django.utils import timezone


from users.models import User
from checkout.models import Order,OrderItem
from .models import Transaction

class UserFilter(django_filters.FilterSet):
    username = django_filters.CharFilter(field_name='username',lookup_expr='icontains',label='User Name')
    is_active = django_filters.ChoiceFilter(
        field_name='is_active',
        label='Active Or Not',
        choices=[
            ('', 'All'),
            ('True', 'Active'),
            ('False', 'Not Active')
        ],
        empty_label=None  # Prevents an additional "---------" option
    )
    
    order_by = django_filters.OrderingFilter(fields=(
 
        ('username', 'username'),
            ('email', 'email'),
          
    ),field_labels={
       
            'username': 'Username',
            'email': 'Email',
          
        },
        choices=[
   
            ('username', 'Username (Ascending)'),
            ('-username', 'Username (Descending)'),
            ('email', 'Email (Ascending)'),
            ('-email', 'Email (Descending)'),
           
        ],
        label='Order By',
        empty_label="All"
        )
   
    class Meta:
        model = User
        fields = ['username', 'email', 'is_active'] 
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)  # initializes FilterSet properly
        
        
        for field in   self.form.fields.values():
           field.widget.attrs.update({
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': field.label, 
            })


class OrderFilter(django_filters.FilterSet):
    id = django_filters.CharFilter(field_name='id',lookup_expr='icontains',label='Order Id')
    class Meta:
        model=Order
        fields = ['status','id',"user__email"]
    def __init__(self,*args ,**kwargs):
        super().__init__(*args,**kwargs)
        for field in self.form.fields.values():
             field.widget.attrs.update({
                'class': 'border highlight-border rounded-md px-3 py-2 text-gray-700 focus:outline-none focus:ring-2 focus:ring-sky-300',
                'placeholder': field.label, 
            })
        
    