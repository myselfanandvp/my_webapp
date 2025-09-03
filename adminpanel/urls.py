from .views import (AdminDashboard,ListUser,UserDetails,OrderList
                    ,OrderDetails,CouponView,DeleteCoupons,SaleReport
                    ,ActivateCoupon,DeactivateCoupon,GeneratePDF,
                    ListTransctions,TranscationDetails,AdminOrderDetail,
                    AdminWalletTranscations,AdminWalletDetails,ChartView,Refferals,OrderReturnAccept,ReturnItems)
from django.urls import path

urlpatterns=[
    path('dashboard/',AdminDashboard.as_view(),name="admin_dashboard_url"),
    path('list/',ListUser.as_view(),name="user_list_url"),
    path('details/<uuid:id>',UserDetails.as_view(),name='user_details_url'),
    path("orders/",OrderList.as_view(),name='order_list_url'),
    path("details/",OrderDetails.as_view(),name='order_details_url'),
    path("coupon/",CouponView.as_view(),name='coupon_url'),
    path('coupon/<uuid:id>/',DeleteCoupons.as_view(),name='delete_coupon_url'),
    path('report/',SaleReport.as_view(),name='salereport_url'),
    path('activate/',ActivateCoupon.as_view(),name='activate_url'),
    path('deactivate/',DeactivateCoupon.as_view(),name='deactivate_url'),
    path('create_report/',GeneratePDF.as_view(),name='report_url'),
    path('transcations/',ListTransctions.as_view(),name='all_transctions_url'),
    path('detail/<uuid:tranid>/',TranscationDetails.as_view(),name='transction_details_url'),
    path('order-detail/<uuid:order_id>/',AdminOrderDetail.as_view(),name='order_detail_url'),
    path('wallet_transcations/',AdminWalletTranscations.as_view(),name='wallet_transcation_url'),
    path('wallet_transcations_detail/<uuid:wallet_id>/',AdminWalletDetails.as_view(),name='wallet_transcation_detail_url'),
    path('chart/',ChartView.as_view(),name='chart_url'),
    path('refferal/',Refferals.as_view(),name='refferal_url'),
    path('return_accept/',OrderReturnAccept.as_view(),name="return_accept_url"),
    path('return_items/',ReturnItems.as_view(),name="return_items_url"),
    
      

  
    
   
]