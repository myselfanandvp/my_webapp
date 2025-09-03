from django.urls import path
from .views import (
    ShippingView,
    OrderConfirmationView,
    DiscountCoupon,RazorpayPaymentHandlerView,OrderFailedView,AddNewAddress,RemoveCoupon,
    
)


urlpatterns = [
    path('shipping/', ShippingView.as_view(), name='shipping_url'),  
   
    path('confirmation/', OrderConfirmationView.as_view(), name='confirmation'),
    path('remove-coupon/', RemoveCoupon.as_view(), name='removecoupon_url'),

    path('discount/', DiscountCoupon.as_view(), name='discount'),   
     path('payment-failed/',OrderFailedView.as_view(), name='order_failed'),
    path('payment-handler/',RazorpayPaymentHandlerView.as_view(), name='payment_handler'),
    path('add_address',AddNewAddress.as_view(),name="add_new_address_url"),
]