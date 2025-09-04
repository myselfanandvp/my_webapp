from django.urls import path
from .views import HomePage,Contactus,Aboutus,Term_And_Condition,Policy,PageNotFound,AllProducts,Carrers,ServerError

urlpatterns =[
    path('',HomePage.as_view(),name="index_page"),
    path('contact/',Contactus.as_view(),name="contact_page"),
    path('about/',Aboutus.as_view(),name="about_page"),
    path('terms/',Term_And_Condition.as_view(),name="term_and_conditon_url"),
    path('policy',Policy.as_view(),name='policy_url'),
    path('pagenotfound/',PageNotFound.as_view(),name="pagenotfound_url"),
    path('products/',AllProducts.as_view(),name="all_products_url"),
    path('carrers/',Carrers.as_view(),name="carrers_url"),
    path('servererror/',ServerError.as_view(),name="server_error_url"),
]