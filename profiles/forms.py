from django import forms
from users.models import User,AddressModel
from django.core.exceptions import ValidationError
import re
# Smaller, more compact input styling
input_field_style = {
    'class': 'bg-gray-100 text-gray-800 text-sm border rounded-lg focus:ring-2 p-1 px-2 h-8 w-full '
}


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'phone_number', 'profile_img']

        widgets = {
            'first_name': forms.TextInput(attrs=input_field_style),
            'last_name': forms.TextInput(attrs=input_field_style),
            'username': forms.TextInput(attrs=input_field_style),
            'email': forms.EmailInput(attrs=input_field_style),
            'phone_number': forms.NumberInput(attrs=input_field_style),
           
        }
        
class AddressForm(forms.ModelForm):
    
    Choices=[
        ('IN', 'India'),
        
    ]
    address_choices=[
        ("home","Home"),
        ("office","Office")
    ]
    country = forms.ChoiceField(choices=Choices,widget=forms.Select())
    type= forms.ChoiceField(choices=address_choices,widget=forms.Select())
    class Meta:
        
        model=AddressModel
        
        fields=['street_address','city','state','postal_code','country','alternate_phone_number','type']
        widgets={'alternate_phone_number':forms.NumberInput(attrs=input_field_style),
                 'postal_code':forms.NumberInput(attrs=input_field_style)
                 ,'street_address':forms.TextInput(attrs=input_field_style),'state':forms.TextInput(attrs=input_field_style)
                 ,'city':forms.TextInput(attrs=input_field_style)
                 }

class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(widget=forms.PasswordInput(attrs=input_field_style),label="Current Password")
    password = forms.CharField(widget=forms.PasswordInput(attrs=input_field_style))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs=input_field_style))
    
    def __init__(self,*args,**kwargs):
        self.user=kwargs.pop('user', None)
        super().__init__(*args,**kwargs)       
        
    def clean_old_password(self):
        old_password = self.cleaned_data.get('old_password')
        if self.user is None:
            raise ValidationError("User must be provided to validate the password")
        if old_password and not self.user.check_password(old_password):
            self.add_error("old_password","Incorrect current password")
        return old_password
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')  
        password_regex = r'^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,}$'
              
        # Validate old password
        if password and confirm_password and password != confirm_password:
            self.add_error("confirm_password","Passwords do not match")      
        # Password complexity validation
        if not re.match(password_regex, password):
            self.add_error("password","Password must include at least one uppercase letter, one lowercase letter, one number, one special character, and be at least 8 characters long.")           
        return cleaned_data
    
    
class ChangeEmail(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs=input_field_style))   
    def clean(self):
        cleaned_data= super().clean()
        email=self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            self.add_error('email',"You can't use this email")
        return cleaned_data
        
    
    
class ProfileOTPForm(forms.Form):
  
    otp = forms.IntegerField(widget=forms.NumberInput(attrs={**input_field_style,'placeholder':"Enter your 6 digit otp"}))     
    
    def clean(self):
        cleaned_data= super().clean()
        otp = cleaned_data.get('otp')
        if otp is not None:
            if len(str(otp)) !=6:
                self.add_error('otp',"OTP must be a 6-digit number")
        return cleaned_data
        
    
