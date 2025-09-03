from django.urls import path
from .views import Wishlist,AddToWishList,DeleteProductWishList
urlpatterns=[
    path('',Wishlist.as_view(),name="wishlist_url"),
    path('addwishlist/<uuid:id>',AddToWishList.as_view(),name="wishlist_add_url"),
    path('removewishlist/<uuid:id>',DeleteProductWishList.as_view(),name="wishlist_remove_url"),
]