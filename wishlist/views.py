from django.shortcuts import render,get_object_or_404,redirect
from django.http import HttpResponse,JsonResponse
from django.views import View
from users.models import User
from products.models import Product,ProductColor
from .models import WishList
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
# Create your views here.

@method_decorator(never_cache, name='dispatch')
class Wishlist(LoginRequiredMixin,View):
    login_url="login_user_url"
    template_name="wishlist/wishlist_list.html"
    def get(self,request):
        wishlist= WishList.objects.filter(user__id=request.user.id)
        return render(request,self.template_name,{'wishlist':wishlist})
    
    
    
@method_decorator(never_cache, name='dispatch')
class AddToWishList(LoginRequiredMixin,View):     
    login_url = "login_user_url"   
    def post(self,request,id):
        color_id=request.POST.get('color')
        colors=ProductColor.objects.filter(id=color_id).first()
        product = get_object_or_404(Product,id=id)
        if WishList.objects.filter(product__id=product.id,color=colors).exists():
             return JsonResponse({'status': 'error', 'message': 'Product is already in wishlist'})
        WishList.objects.create(user=request.user,product=product,color=colors)
        return JsonResponse({'status': 'success', 'message': 'Product added to the wishlist'})


@method_decorator(never_cache, name='dispatch')
class DeleteProductWishList(LoginRequiredMixin,View):    
    login_url = "login_user_url"
    def post(self,request,id):
        product = get_object_or_404(WishList,id=id)
        if product.delete():
            messages.success(request,"Product removed")
            return redirect('wishlist_url')
        