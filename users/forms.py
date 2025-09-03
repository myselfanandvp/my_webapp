from django import forms
from .models import User
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import re

# Reusable field styles
input_field_style = {
    'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'
}

image_field_style = {
    'class': 'block w-full p-2.5 text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 dark:text-gray-400 focus:outline-none dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400'
}

field_style = {
    'class': 'w-10 h-10 sm:w-12 sm:h-12 md:w-14 md:h-14 text-center text-xl sm:text-2xl font-extrabold text-slate-900 bg-slate-100 border border-transparent hover:border-slate-200 appearance-none rounded p-2 sm:p-3 md:p-4 outline-none focus:bg-white focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100',
    'inputmode': 'numeric',
    'autocomplete': 'off',
    "maxlength": "1",
    "pattern": "[0-9]*"

}


class SignupForm(forms.ModelForm):
    confirm_pass = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirm password',
            **input_field_style
        }),
        label="Confirm Password"
    )
    referral_code = forms.CharField(
        required=False,
        label="Have a Referral Code? (Optional)",  
        widget=forms.TextInput(attrs={**input_field_style, "placeholder": "Enter your referral code"})
    )

    class Meta:
        model = User
        fields = ['username','email', 'password', 'confirm_pass']
        widgets = {
            'username':forms.TextInput(attrs={**input_field_style,"placeholder":"Enter your username"}),
            'referral_code':forms.TextInput(attrs={**input_field_style,"placeholder":"Enter your referal code"}),
            'email': forms.EmailInput(attrs={**input_field_style, "placeholder": "Email address"}),
            'password': forms.PasswordInput(attrs={**input_field_style, "placeholder": "Enter the password"}),
        }
       

    def clean_password(self):

        password = self.cleaned_data.get('password')
        if not password:
            raise ValidationError(_("Password is required."))

        # Password complexity validation
        password_regex = r'^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,}$'
        if not re.match(password_regex, password):
            raise ValidationError(
                _("Password must include at least one uppercase letter, one lowercase letter, one number, one special character, and be at least 8 characters long."),
                code='password_not_complex'
            )
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        referral_code = cleaned_data.get('referral_code',None)
        if referral_code:
            if not User.objects.filter(referral_code=referral_code).exists():      
                self.add_error('referral_code',"Given code is invalid")
        
        confirm_password = cleaned_data.get('confirm_pass')
        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_pass', "Passwords do not match.")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])  # hashes the password
        referral_code = self.cleaned_data.get("referral_code")
        if referral_code:
            user._signup_referral_code = referral_code   
        
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):

    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={**input_field_style, "placeholder": "Email address"})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={**input_field_style, "placeholder": "Enter your password"}))


class Change_Password_Form(forms.Form):

    password1 = forms.CharField(widget=forms.PasswordInput(
        attrs={**input_field_style, "placeholder": "New password", "autocomplete": "off"}))
    password2 = forms.CharField(widget=forms.PasswordInput(
        attrs={**input_field_style, "placeholder": "Confirm Password", "autocomplete": "off"}))


class OTPVerificationForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for i in range(1, 7):  # otp_1 to otp_6
            self.fields[f'otp_{i}'] = forms.CharField(
                max_length=1,
                required=True,
                widget=forms.TextInput(attrs=field_style)
            )

    def get_otp(self):
        otp_str = ''.join([
            self.cleaned_data.get(f'otp_{i}', '') for i in range(1, 7)
        ])

        if not otp_str.isdigit():
            return None  # Invalid format

        return int(otp_str)

class ResetPasswordForm(forms.Form):

    email = forms.EmailField(widget=forms.EmailInput(
        attrs={**input_field_style, "placeholder": "Enter your email id"}))


# Admin Forms

class Admin_Login_Form(forms.Form):

    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={**input_field_style, "placeholder": "Email address"})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={**input_field_style, "placeholder": "Enter your password"})
    )
