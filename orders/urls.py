from django.urls import path
from .views import OrderReviewView,OrderDetail,GeneratePDF,OrderReturn

urlpatterns=[
    # User Profile urls    
  
    path('', OrderReviewView.as_view(), name='orders_url'),
    path('Details/', OrderDetail.as_view(), name='order_detail_url'),
    path('report/', GeneratePDF.as_view(), name='order_report_url'),    
    path('return/',OrderReturn.as_view(),name="return_url"),

]