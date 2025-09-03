from .views import SignupUser,LoginUser,ChangePassword,OTP_Validation,ForgotPassword,LogoutUser,ResendOTP,LoginAdmin,Signup_OTP,BlockUser
from django.urls import path
urlpatterns=[
    #User Urls
    path('signup/',SignupUser.as_view(),name="signup_user_url"),
    path('signup_otp/',Signup_OTP.as_view(),name='signup_otp_url'),
    path('login/',LoginUser.as_view(),name="login_user_url"),
    path('logout/',LogoutUser.as_view(),name="logout_user_url"),
    path('change-password/',ChangePassword.as_view(),name="forgot_change_password_url"),
    path('otp/',OTP_Validation.as_view(),name="otp_validation_url"),
    path('resendotp/',ResendOTP.as_view(),name="resendotp_url"),
    path('forgot-password/',ForgotPassword.as_view(),name="forgot_password_url"),  
    
       

    # Admin Urls
    path('admin/login/',LoginAdmin.as_view(),name="login_admin_url"),
    path('admin/block/<uuid:id>',BlockUser.as_view(),name="block_admin_url"),
    
 
    
    
]