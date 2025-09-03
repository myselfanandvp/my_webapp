from django.urls import path
from .views import CartList,AddtoCart,DeleteCartItem,DecrementQunatity,IncrementQuantity
urlpatterns=[
    path('',CartList.as_view(),name='list_cart_url'),
    path('add/<uuid:id>',AddtoCart.as_view(),name='add_cart_url'),
    path('delete/<uuid:id>',DeleteCartItem.as_view(),name='delete_cart_url'),
    path('increment/<uuid:id>',IncrementQuantity.as_view(),name='increment_cart_url'),
    path('decrement/<uuid:id>',DecrementQunatity.as_view(),name='decrement_cart_url'),
]