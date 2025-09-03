from django.urls import path
from .views import (Profile_Edit_View,Add_ProfileAddress,ProfileAddress,
                    EditAddress,DeleteAddress,ProfileView,ProfileChangePasswordView,
                    ChangeEamilView,OTP_ValidationView,ResentOTP,ProfieWalletView,DeleteAccount,
                    ProfileCoupon,Add_ProductReview,WalletPaymentverfiy,PaymentFailedView,ReferrAndEarn)

urlpatterns=[
        # User Profile urls    
    path("profile/",ProfileView.as_view(),name="user_profile_url"),
    path("editprofile/",Profile_Edit_View.as_view(),name="user_profile_edit_url"),    
    path("add/",Add_ProfileAddress.as_view(),name="add_user_address_url"),
    path("address/",ProfileAddress.as_view(),name="user_address_url"),
    path("edit/<uuid:id>",EditAddress.as_view(),name="edit_address_url"),
    path("delete/<uuid:id>",DeleteAddress.as_view(),name="delete_address_url"),
    path("changepassword/",ProfileChangePasswordView.as_view(),name="change_password_url"),
    path("changeemail/",ChangeEamilView.as_view(),name="change_email_url"),
    path("otp/",OTP_ValidationView.as_view(),name="otp_url"),
    path("resentotp/",ResentOTP.as_view(),name="resentotp_url"),
    path("wallet/",ProfieWalletView.as_view(),name="wallet_url"),
    path("delete_account/",DeleteAccount.as_view(),name="delete_account_url"),
    path("coupons/",ProfileCoupon.as_view(),name="coupons_url"),
    path("review/",Add_ProductReview.as_view(),name="review_url"),
    path("verfiy-payment/",WalletPaymentverfiy.as_view(),name="wallet_verify_payment"),
    path("payment-failed/",PaymentFailedView.as_view(),name="payment_failed_url"),
    path("referals/",ReferrAndEarn.as_view(),name="referral_url"),
  
 
]