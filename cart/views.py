from django.shortcuts import render,get_object_or_404,redirect
from django.views import View
from users.models import User
from products.models import Product,ProductColor
from .models import Cart
from wishlist.models import WishList
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal
# Create your views here.
@method_decorator(never_cache, name='dispatch')
class CartList(LoginRequiredMixin,View):
    login_url='login_user_url'
    template_name="cart/cart.html"
    breadcrumb="Callsign"
    def get(self,request):
        cart_items = Cart.objects.filter(user__id=request.user.id)
        total_amount=sum([i.total_price for i in cart_items])+50
               
        return render(request,self.template_name,{'cart':cart_items ,'cart_total':total_amount})
    
@method_decorator(never_cache, name='dispatch')
class AddtoCart(LoginRequiredMixin,View):
    login_url='login_user_url'
    def post(self,request,id):
        product = get_object_or_404(Product,id=id)
        user = get_object_or_404(User,id=request.user.id)
        color_id=request.POST.get('color','')
        color = get_object_or_404(ProductColor,id=color_id)
        cart,created=Cart.objects.get_or_create(user=user,product=product,color=color)   
        WishList.objects.filter(product__id=id,color=color,user=user).delete()        
        count= cart.increment_quantity()
        if count==5:
            return JsonResponse({"status":"error","message":"You reached you limit!"})  
        
            
        return JsonResponse({"status":'success',"message":"product added"})
        
    
@method_decorator(never_cache, name='dispatch')
class DeleteCartItem(View):
    def post(self,request,id):
        cart = get_object_or_404(Cart,id=id)
        cart.remove_product()
        return redirect("list_cart_url")
    
    
@method_decorator(never_cache, name='dispatch')  
class IncrementQuantity(LoginRequiredMixin,View):
    login_url='login_user_url'
    def post(self,request,id):
        cart = get_object_or_404(Cart,id=id)
        quantity = cart.increment_quantity()      
        total_price = cart.total_price
        cart_items = Cart.objects.filter(user__id=request.user.id)
        total_amount=sum([i.total_price for i in cart_items])+Decimal("50.00")
        return JsonResponse({"status":'success','quantity':'{}'.format(quantity),"total_price":total_price,"total_amount":total_amount})
    
    
@method_decorator(never_cache, name='dispatch')
class DecrementQunatity(LoginRequiredMixin,View):
    login_url='login_user_url'
    def post(self,request,id):
        cart = get_object_or_404(Cart,id=id)
        quantity = cart.decrement_quantity()       
        total_price = cart.total_price       
        cart_items = Cart.objects.filter(user__id=request.user.id)
        total_amount=sum([i.total_price for i in cart_items])+Decimal("50.00")
        return JsonResponse({"status":'success','quantity':'{}'.format(quantity),"total_price":total_price,'total_amount':total_amount})
        
        
