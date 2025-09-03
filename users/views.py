from .forms import SignupForm, LoginForm, Change_Password_Form, OTPVerificationForm, ResetPasswordForm, Admin_Login_Form
from random import randint
from .models import User
from django.shortcuts import render, redirect,get_object_or_404
from django.views import View
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse,HttpResponse
from django.core.mail import send_mail
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from datetime import datetime, timedelta
from django.conf import settings
from django.urls import reverse
from allauth.account.adapter import DefaultAccountAdapter




# OTP generator helper
def generate_and_send_otp(**kwargs):
    otp = randint(100000, 999999)
    request = kwargs['request']
    request.session['otp'] = otp
    request.session['otp_created_at'] = datetime.now().isoformat()
    request.session.set_expiry(300)  # Enforce 5-minute expiry
    user = request.session.get("user_name") or "User"
    # Compose email
    subject = "Your One-Time Password for Password Reset"
    message = f"""
    Dear {user},

        Your one-time password (OTP) is: {otp}

        Please use this code to complete your password reset. This code is valid for 5 minutes.

        If you did not request this, please ignore this message.

        Best regards,
        WaveLift Support Team

    """
    

    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [request.session.get('user_email')],
        fail_silently=False
    )


def get_session_user(request):
    email = request.session.get('user_email')
    if not email:
        return None
    return User.objects.filter(email=email).first()


# Create your views here.


# User Views

@method_decorator(never_cache, name='dispatch')
class LoginUser(View):
    template_name = "user/user_login_page.html"

    def get(self, request):
        if request.user.is_authenticated and request.user.is_superuser:
            return redirect("admin_dashboard_url")
        elif request.user.is_authenticated:
            return redirect("index_page")
        request.session['page'] = 1
        form = LoginForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            email, password = form.cleaned_data.get(
                'email'), form.cleaned_data.get('password')
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(user=user, request=request)
                if request.user.is_superuser:
                    return redirect('admin_dashboard_url')
                return redirect("all_products_url")
            else:
                form.add_error("password", "Password or email is wrong")

        return render(request, self.template_name, {"form": form})


@method_decorator(never_cache, name='dispatch')
class SignupUser(View):

    template_name = 'user/user_signup_page.html'

    def get(self, request):
        form = SignupForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = SignupForm(request.POST)
        if form.is_valid():
            request.session['user'] = form.cleaned_data
            request.session['user_email'] = form.cleaned_data.get('email')
            generate_and_send_otp(request=request)
            request.session['otp_created_at'] = datetime.now().isoformat()
            messages.success(request, "Enter  otp that sent to you email")
            return redirect("signup_otp_url")
            # messages.success(request,'Your account has been created successfully. Please log in to continue.')
            # return redirect('login_user_url')
        return render(request, self.template_name, {"form": form})


@method_decorator(never_cache, name='dispatch')
class Signup_OTP(View):
    template_name = 'user/otp_validation.html'

    def get(self, request):
        form = OTPVerificationForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = OTPVerificationForm(request.POST)
        if form.is_valid():
            session_otp = request.session.get('otp')
            user_otp = form.get_otp()

            if user_otp is None:
                form.add_error(
                    None, "The OTP format is invalid. Please enter 6 digits.")
                return render(request, self.template_name, {'form': form})

            # Track attempts
            attempts = request.session.get('otp_attempts', 0)
            if attempts >= 5:
                form.add_error(
                    None, "Too many incorrect attempts. Please request a new OTP.")
                return render(request, self.template_name, {"form": form})

            # Check if OTP is missing
            if not session_otp or not user_otp:
                form.add_error(
                    None, "OTP has expired or is invalid. Please request a new one.")
                return render(request, self.template_name, {'form': form})

            # Check for expiration (5 minutes)
            otp_created_at_str = request.session.get('otp_created_at')
            if otp_created_at_str:
                otp_created_at = datetime.fromisoformat(otp_created_at_str)
                if datetime.now() > otp_created_at + timedelta(minutes=5):
                    request.session.pop('otp', None)
                    request.session.pop('otp_created_at', None)
                    form.add_error(
                        None, "OTP has expired. Please request a new one.")
                    return render(request, self.template_name, {'form': form})
            else:
                form.add_error(
                    None, "OTP session info is missing. Please request a new one.")
                return render(request, self.template_name, {'form': form})

            # Check if OTP matches
            if int(session_otp) == user_otp:
                form = SignupForm(request.session.get('user'))
                form.save()
                messages.success(
                    request, "Your account has been created successfully. Please log in to continue.")
                request.session.pop('otp', None)
                request.session.pop('otp_created_at', None)
                request.session.pop('user', None)
                return redirect('login_user_url')

            request.session['otp_attempts'] = attempts + 1
            form.add_error(None, "Entered OTP is incorrect.")

        return render(request, self.template_name, {'form': form})


@method_decorator(never_cache, name='dispatch')
class LogoutUser(LoginRequiredMixin, View):
    def post(self, request):
        is_admin = request.user.is_superuser  # Store the flag before logout
        logout(request)
        messages.success(request, "Logged out successfully")
        if is_admin:
            return redirect("login_admin_url")
        return redirect("login_user_url")


@method_decorator(never_cache, name='dispatch')
class ChangePassword(View):
    template_name = 'user/change_password.html'
    def get(self, request):   
        if not request.session.get('user_email'):
            return redirect('forgot_password_url')  # or your OTP page
        form = Change_Password_Form()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = Change_Password_Form(request.POST)
        if form.is_valid():
            password, confirm_password = form.cleaned_data['password1'], form.cleaned_data['password2']
            if password == confirm_password and (password is not None and confirm_password is not None):
                user = get_session_user(request)
                user.set_password(form.cleaned_data['password1'])
                user.save()
                messages.success(
                    request, "Your password has been updated successfully.")
                if user.is_superuser:
                    request.session.pop('user_email', None)
                    request.session.pop('user_name', None)
                    return redirect("login_admin_url")
                else:
                    return redirect("login_user_url")

            form.add_error("password2", "Passwords do not match.")

        return render(request, self.template_name, {"form": form})


@method_decorator(never_cache, name='dispatch')
class OTP_Validation(View):
    template_name = 'user/otp_validation.html'

    def get(self, request):
        if not request.session.get('user_email',None):
            return redirect('forgot_password_url')

        form = OTPVerificationForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = OTPVerificationForm(request.POST)

        if form.is_valid():
            otp_input = form.get_otp()
            if otp_input is None:
                form.add_error(
                    None, "The OTP format is invalid. Please enter 6 digits.")
                return render(request, self.template_name, {'form': form})

            session_otp = request.session.get('otp')
            otp_created_at_str = request.session.get('otp_created_at')


            # Check if session data is missing
            if not session_otp or not otp_created_at_str:
                form.add_error(
                    None, "OTP session info is missing. Please request a new one.")
                return render(request, self.template_name, {'form': form})

            # Parse the stored OTP time
            try:
                otp_created_at = datetime.fromisoformat(otp_created_at_str)
            except ValueError:
                form.add_error(
                    None, "Corrupted OTP timestamp. Please request a new one.")
                return render(request, self.template_name, {'form': form})

            # Check for expiration (5 minutes)
            if datetime.now() > otp_created_at + timedelta(minutes=5):
                request.session.pop('otp', None)
                request.session.pop('otp_created_at', None)
                form.add_error(
                    None, "OTP has expired. Please request a new one.")
                return render(request, self.template_name, {'form': form})

            # Check attempts
            attempts = request.session.get('otp_attempts', 0)
            if attempts >= 5:
                form.add_error(
                    None, "Too many incorrect attempts. Please request a new OTP.")
                return render(request, self.template_name, {"form": form})

            # Compare OTPs
            if str(session_otp) == str(otp_input):
                # OTP is valid
                request.session.pop('otp', None)
                request.session.pop('otp_created_at', None)
                request.session.pop('otp_attempts', None)
                return redirect('forgot_change_password_url')
            else:
                # OTP is wrong
                request.session['otp_attempts'] = attempts + 1
                form.add_error(None, "Entered OTP is incorrect.")

        return render(request, self.template_name, {'form': form})


@method_decorator(never_cache, name='dispatch')
class ForgotPassword(View):
    template_name = 'user/reset_password_email.html'

    def get(self, request):
        form = ResetPasswordForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):

        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            user = User.objects.filter(email=form.cleaned_data['email']).first()
            if user is not None:
                request.session['user_email'] = user.email
                request.session['user_name'] = user.username
                request.session.set_expiry(300)
                generate_and_send_otp(request=request)
                request.session.pop('page', None)
                messages.success(request, "OTP has been sent to your email.")

                return redirect('otp_validation_url')

            form.add_error("email", "Email you are given is wrong")

        return render(request, self.template_name, {"form": form})


@method_decorator(never_cache, name='dispatch')
class ResendOTP(View):
    def post(self, request):
        request.session.pop('otp_attempts', None)  # Reset failed attempts
        generate_and_send_otp(request=request)
        return JsonResponse({'status': 'success', 'message': 'OTP resent successfully!'})


# Admin Views
@method_decorator(never_cache, name='dispatch')
class LoginAdmin(View):
 
    template_name = 'admin/admin_login.html'
    
    def get(self, request):
        if request.user.is_authenticated:
            return redirect("admin_dashboard_url")
        request.session['page'] = 0
        form = Admin_Login_Form()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = Admin_Login_Form(request.POST)
        if form.is_valid():
            email, password = form.cleaned_data.get(
                'email'), form.cleaned_data.get('password')
            user = get_object_or_404(User,email=email)
            if user.is_superuser:
                admin = authenticate(request, username=email, password=password)
                if admin is not None:
                    login(request, admin)
                    return redirect('admin_dashboard_url')
                form.add_error("password", "Username or Password is wrong!")
                return render(request, self.template_name, {"form": form})
            
            messages.error(request, "An unexpected error occurred. Please contact support.")
        return render(request, self.template_name, {"form": form})
       


@method_decorator(never_cache, name='dispatch')
class BlockUser(LoginRequiredMixin,View):
    
    def post(self,request,id):
        user = User.objects.filter(id=id).first()
        if user and user.is_active:
            user.is_active=0
            user.save(update_fields=['is_active'])
            return JsonResponse({"message":"User is blocked"})
        elif user and not user.is_active:
            user.is_active=1
            user.save(update_fields=['is_active'])
            return JsonResponse({"message":"User is Unblocked"})

        return JsonResponse({"message":"Something went wrong"})
    
