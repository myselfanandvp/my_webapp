from django import forms
from .models import Coupon

class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = ['code', 'discount', 'expiry_date','max_uses_per_user', 'min_purchase']
        widgets = {
            'code': forms.TextInput(attrs={
                'class': 'mt-1 block w-full border border-gray-300 rounded-md p-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'e.g.,HEADPHONE5K'
            }),
            'discount': forms.NumberInput(attrs={
                'class': 'mt-1 block w-full border border-gray-300 rounded-md p-2 focus:ring-blue-500 focus:border-blue-500',
                'step': '0.01',
                'min': '0.01',
                'max': '100.00',
                'placeholder': 'e.g., 15.00'
            }),
            'expiry_date': forms.DateInput(attrs={
                'class': 'mt-1 block w-full border border-gray-300 rounded-md p-2 focus:ring-blue-500 focus:border-blue-500',
                'type': 'date'
            }),
            'min_purchase': forms.NumberInput(attrs={
                'class': 'mt-1 block w-full border border-gray-300 rounded-md p-2 focus:ring-blue-500 focus:border-blue-500',
                'step': '0.01',
                'min': '0.00',
                'placeholder': 'e.g., 5000.00'
            }),
            'max_uses_per_user': forms.NumberInput(attrs={
                'class': 'mt-1 block w-full border border-gray-300 rounded-md p-2 focus:ring-blue-500 focus:border-blue-500',
                'step': '0.01',
                'min': '0.00',
                'placeholder': 'e.g., 5000.00'
            }),
        }
        labels = {
            'code': 'Coupon Code',
            'discount': 'Discount (%)',
            'expiry_date': 'Expiry Date',
            'min_purchase': 'Minimum Purchase (₹)',
            'max_uses_per_user':'Max Use Count',
        }
        help_texts = {
            'code': 'Enter a unique coupon code (e.g., SAVE20).',
            'discount': 'Discount percentage between 0.01 and 100.00.',
            'expiry_date': 'Select the date when the coupon expires.',
            'min_purchase': 'Minimum purchase amount required to apply the coupon.',
            'max_uses_per_user': 'Maximum count per user to apply the coupon.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.error_messages = {'required': f'{field.label} is required.'}