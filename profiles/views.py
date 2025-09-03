from django.shortcuts import render,redirect,get_object_or_404
from django.views import View
from users.models import User,AddressModel
from .forms import ProfileForm,AddressForm,ChangePasswordForm,ChangeEmail,ProfileOTPForm
from django.contrib import messages
from django import template
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect,JsonResponse,HttpResponse
from django.contrib.auth import update_session_auth_hash
from random import randint
from datetime import datetime, timedelta
from django.core.mail import send_mail
from django.conf import settings
from checkout.models import Order
from django.contrib.auth import logout
from .models import Wallet,WalletTransaction
from decimal import Decimal
from products.models import ProductReview,Product
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import razorpay
from django.conf import settings
import json
from adminpanel.models import Coupon
from django.db.models.aggregates import Sum,Avg,Min,Max
from users.models import ReferralRelationship

client = razorpay.Client(auth=(settings.RAZOR_KEY_ID,settings.RAZOR_KEY_SECRET))

#Helpers

# OTP generator helper
def generate_and_send_otp(**kwargs):
    otp = randint(100000, 999999)
    request = kwargs['request']
    request.session['otp'] = otp
    request.session['otp_created_at'] = datetime.now().isoformat()
    request.session.set_expiry(300)  # Enforce 5-minute expiry
    user = request.user.username  or "User"
    # Compose email
    subject = "Your One-Time Password for Email Change"
    message = f"""
    Dear {user},

        Your one-time password (OTP) is: {otp}

        Please use this code to complete your email reset. This code is valid for 5 minutes.

        If you did not request this, please ignore this message.

        Best regards,
        WaveLift Support Team

    """

    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [kwargs.get('new_email')],
        fail_silently=False
    )





# Create your views here.

# Profile page views
@method_decorator(never_cache, name='dispatch')
class ProfileView(LoginRequiredMixin,View):
    login_url="login_user_url"
    template_name = "profiles/user_profile.html"
    def get(self,request):
        user = User.objects.filter(id=request.user.id).first()
        return render(request,self.template_name,{'user':user})


@method_decorator(never_cache, name='dispatch')
class Profile_Edit_View(LoginRequiredMixin,View):
    login_url="login_user_url"
    template_name = "profiles/user_profile_edit.html"

    def get(self, request):
        user = User.objects.filter(id=request.user.id).first()
        form = ProfileForm(instance=user)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        user = request.user
        form = ProfileForm(request.POST, request.FILES, instance=user)

        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
          
            return redirect('user_profile_url')
        else:
            messages.error(request, "Please correct the errors below.")

        return render(request, self.template_name, {'user': user, 'form': form})

@method_decorator(never_cache, name='dispatch')
class Add_ProfileAddress(LoginRequiredMixin,View):
    login_url="login_user_url"
    template_name="profiles/profile_address_add_or_edit.html"
    def get(self,request):
        form = AddressForm()
        return render(request,self.template_name,{'form':form})
    def post(self,request):
        form = AddressForm(request.POST)
        if form.is_valid():
            user = User.objects.filter(id=request.user.id).first()
            if user.phone_number!=form.cleaned_data.get('alternate_phone_number'):
                address = form.save(commit=False)
                address.user=user
                address.save()
                messages.success(request, "Address added successfully.")                
                return redirect('user_address_url')
            else:
                form.add_error('alternate_phone_number', "The alternate number shouldn't be the same as your primary number.")
        return render(request,self.template_name,{'form':form})
    
@method_decorator(never_cache, name='dispatch')
class ProfileAddress(LoginRequiredMixin,View):
    login_url="login_user_url"
    template_name = 'profiles/profile_address.html'
    def get(self,request):
        user_address = AddressModel.objects.filter(user__id=request.user.id)
        return render(request,self.template_name,{"addr":user_address})


@method_decorator(never_cache, name='dispatch')
class EditAddress(LoginRequiredMixin,View):
    login_url="login_user_url"
    template_name="profiles/profile_address_add_or_edit.html"    
    def get(self,request,id):
        user_address = get_object_or_404(AddressModel,id=id,user=request.user)
        form = AddressForm(instance=user_address)
        # form.fields.pop('type')
        return render(request,self.template_name,{'form':form , 'is_edit':True})
    
    def post(self,request,id):        
        address = get_object_or_404(AddressModel,id=id,user=request.user.id)
        form = AddressForm(request.POST,instance=address)
        # form.fields.pop('type')
        if form.is_valid():
            if request.user.phone_number != form.cleaned_data.get('alternate_phone_number'):
                form.save()
                messages.success(request, "Address updated successfully.")
                return redirect('user_address_url')
            else:
                form.add_error('alternate_phone_number', "The alternate number cannot be the same as your primary number.")
        else:
            messages.error(request, "Please correct the errors below.")
            
        return render(request, self.template_name, {'form': form,'is_edit':True})

        
@method_decorator(never_cache, name='dispatch')
class DeleteAddress(LoginRequiredMixin,View):
    login_url='login_user_url'
    def post(self,request,id):
        address = get_object_or_404(AddressModel,id=id)        
        address.delete()
        messages.success(request,"Address deleted successfully")
        return redirect('user_address_url')

@method_decorator(never_cache, name='dispatch')  
class ProfileChangePasswordView(LoginRequiredMixin,View):
    login_url='login_user_url'
    template_name="profiles/profile_changepassword.html"
    def get(self,request):
        form = ChangePasswordForm()        
        return render(request,self.template_name,{'form':form})
    
    def post(self,request):
        form = ChangePasswordForm(request.POST,user=request.user)
        if form.is_valid():
            if form.clean_old_password(): 
                request.user.set_password(form.cleaned_data.get('password'))
                request.user.save()
                update_session_auth_hash(request, request.user)
                messages.success(request,"Your password as been changed successfully.")              
                return redirect("user_profile_url")
        return render(request,self.template_name,{"form":form})
    
@method_decorator(never_cache, name='dispatch')    
class ChangeEamilView(LoginRequiredMixin,View):
    login_url='login_user_url'
    template_name = 'profiles/profile_email_change.html'
    def get(self,request):
        form = ChangeEmail()
        return render(request,self.template_name,{'form':form})
    
    def post(self,request):
        form = ChangeEmail(request.POST)
        if form.is_valid():
            request.session['new_email']=form.cleaned_data['email']
            generate_and_send_otp(request=request,new_email=form.cleaned_data['email'])
            messages.success(request,"OTP sent to the email address.")
            return redirect('otp_url')
        return render(request,self.template_name,{'form':form})
    
@method_decorator(never_cache, name='dispatch')  
class OTP_ValidationView(LoginRequiredMixin,View):
    login_url = "login_user_url"
    template_name= 'profiles/profile_otp_validation.html'
    def get(self,request):
        form = ProfileOTPForm()
        return render(request,self.template_name,{'form':form})
    def post(self,request):
        form = ProfileOTPForm(request.POST)
        if form.is_valid():
            otp = request.session.get('otp')
            if form.cleaned_data['otp']==otp:            
               request.user.email= request.session.get('new_email')
               request.user.save()
               update_session_auth_hash(request, request.user)
               request.session.pop('new_email',None)
               request.session.pop('otp',None)
               messages.success(request,"Email has be changed")
               return redirect('user_profile_url')
            form.add_error('otp', 'OTP invalid')
        
        return render(request,self.template_name,{'form':form})
    
@method_decorator(never_cache, name='dispatch')
class ResentOTP(View):
    def post(self, request):
        new_email = request.session.get('new_email')
        if not new_email:
            return JsonResponse({"message": "No email found"}, status=400)

        try:
            generate_and_send_otp(request=request, new_email=new_email)
          
            return JsonResponse({"message": "New OTP has been sent"})
        except Exception as e:
            return JsonResponse({"message": f"Error: {str(e)}"}, status=500)  
        
@method_decorator(csrf_exempt,name='dispatch')    
@method_decorator(never_cache, name='dispatch')
class ProfieWalletView(LoginRequiredMixin,View):
    login_url = "login_user_url"
    template_name = "profiles/profile_wallet.html"
    key = settings.RAZOR_KEY_ID
    def get(self, request):
        wallet ,created = Wallet.objects.get_or_create(user=request.user)       
        
        return render(request,self.template_name,{'wallet':wallet,"key":self.key})

    def post(self, request):
        wallet ,_ = Wallet.objects.get_or_create(user=request.user)
        amount_str = request.POST.get("amount")
        amount = int(amount_str)
        action = request.POST.get('action')
        
        
        
        try:
            if action == "add":
                client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
                amount_in_paise = amount*100 # Razorpay expects amount in paise
                razorpay_order = client.order.create({
                "amount": amount_in_paise,
                "currency": "INR",
                "payment_capture": 1,  # Auto-capture
                "notes": {
                    "user_id": str(request.user.id),
                    "purpose": "Add to wallet"
                }
                })
                return JsonResponse({
                'action':'add',
                "status": "success",
                "order_id": str(razorpay_order['id']),
                "amount": amount_in_paise,
                "currency": "INR",
                "key": str(self.key)
                })

                # wallet.deposit(amount, description="Added money to wallet")
                # return JsonResponse({"message":f"₹{amount:.2f} added to your wallet.",'status':"success","balance":wallet.balance})
            elif action == "withdraw":
                if amount>wallet.balance:
                    return JsonResponse({"action":'withdraw',"message":f"₹{amount:.2f} cannot withdrawn from your wallet.",'status':"error","balance":wallet.balance})
                
                wallet.withdraw(amount, description="Withdrawn from wallet")
                return JsonResponse({'action':'withdraw',"message":f"₹{amount:.2f} withdrawn from your wallet.",'status':"success","balance":wallet.balance})
               
            else:
                return JsonResponse({"message":"Unknown action.",'status':"error"})
                
                
        except ValueError as e:
            return JsonResponse({"message":f"Unknown action: {str(e)}",'status':"error"})
    
        


@method_decorator(never_cache, name='dispatch')
class DeleteAccount(LoginRequiredMixin,View):
    login_url = "login_user_url"
    template_name = "profiles/account_delete.html"
    def get(self,request):
        return render(request,self.template_name,{})
    def post(self,request):
        password = request.POST.get('password')
        user = request.user
        if user.check_password(password): 
            try:           
                user.delete()
                logout(request)
                messages.success(request, "Your account has been successfully deleted.")
                return redirect('index_page')  #
            except Exception as e:
                messages.error(request, f"An error occurred while deleting your account: {str(e)}")            
     
        else:
            messages.error(request, "Incorrect password. Please try again.")
        return HttpResponseRedirect(request.path)
    
@method_decorator(never_cache, name='dispatch')    
class ProfileCoupon(LoginRequiredMixin,View):
    template_name="profiles/profile_coupons.html"
    def get(self,request):
        coupons = Coupon.objects.filter(is_active=True)
        return render(request,self.template_name,{'coupons':coupons})
    
    
class ReferrAndEarn(View):
    template_name = "profiles/referandearn.html"
    
    def get(self,request):
        total_earnings = WalletTransaction.objects.filter(wallet__user=request.user,transaction_type='referral').aggregate(total_amount=Sum('amount'))['total_amount']
        
        referred_users = ReferralRelationship.objects.filter(referrer=request.user)      
    

        return render(request,self.template_name,{'total_earnings':total_earnings,'referred_users':referred_users})
    
    def post(self,request):
        pass
    
    
    
    
    
    
    
@method_decorator(never_cache, name='dispatch') 
class Add_ProductReview(LoginRequiredMixin,View):
    template_name = "profiles/product_review.html"    
    def get(self,request):
        product_id = request.GET.get('product_id')
        product = get_object_or_404(Product,id=product_id)
        return render(request,self.template_name,{'product':product})
    
    def post(self,request):
        product_id = request.POST.get('product_id')
        rating = request.POST.get('rating')
        review = request.POST.get('review')
        product = get_object_or_404(Product,id=product_id) 
        # Validate input
        if not rating or not review:
            messages.error(request, "Please provide both a rating and a review.")
            return redirect('review_url', product_id=product_id)

        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                raise ValueError
        except (ValueError, TypeError):
            messages.error(request, "Invalid rating. Please select a rating between 1 and 5.")
            return redirect('review_url', product_id=product_id)
               
        obj,created = ProductReview.objects.get_or_create(product=product,user=request.user,rating=rating,review=review)
    
                
        messages.success(request, f"Your review has been {'added' if created else 'updated'} successfully.")    
        return redirect('orders_url')
    
@method_decorator(csrf_exempt,name='dispatch')
class WalletPaymentverfiy(LoginRequiredMixin,View):
    def post(self,request): 
       
        data = json.loads(request.body)
        razorpay_payment_id = data.get("razorpay_payment_id")
        razorpay_order_id = data.get("razorpay_order_id")
        razorpay_signature = data.get("razorpay_signature")
        amount_str = data.get("amount")  
        client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
        try:
            params_dict = {
                    'razorpay_order_id': razorpay_order_id,
                    'razorpay_payment_id': razorpay_payment_id,
                    'razorpay_signature': razorpay_signature
                }
            
            client.utility.verify_payment_signature(params_dict)
            amount = Decimal(amount_str)
            wallet, _ = Wallet.objects.get_or_create(user=request.user)       
            wallet.deposit(amount, description="Online payment",razorpay_order_id=razorpay_order_id,
                           razorpay_payment_id=razorpay_payment_id,razorpay_signature=razorpay_signature)  
                  
            return JsonResponse({
                            "status": "success",
                            "message": f"₹{amount:.2f} added to your wallet.",
                            "balance": wallet.balance
                        })  
        
        except razorpay.errors.SignatureVerificationError:
            return JsonResponse({"status": "error", "message": "Payment verification failed."}) 
        
        
class PaymentFailedView(LoginRequiredMixin,View):
    login_url='login_user_url'
    template_name = 'profiles/wallet_payment_failed.html'
    def get(self,request):
        return render(request,self.template_name)     
    
    

 