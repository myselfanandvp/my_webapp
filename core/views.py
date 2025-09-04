from django.shortcuts import render,redirect,get_object_or_404
from django.views import View
from products.models import Product
from django.db.models.aggregates import Max,Min
from .filter import Myfilter
from django.core.paginator import Paginator
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
# Create your views here.


class  HomePage(View):
    template_name= 'core/index.html'
    view_name = 'home'  # Match with URL name
   

    def get(self,request):
        if request.user.is_superuser:
            return redirect("admin_dashboard_url")
        products = Product.objects.all()
        new_arrivals = Product.objects.select_related('category').filter(category__name__istartswith="New Arrival")

        return render(request,self.template_name,{'products':products,'new_arrivals':new_arrivals})
    
class Contactus(View):
    template_name = 'core/contact.html'
    def get(self,request):
        return render(request,self.template_name,{})
    
class Aboutus(View):
    template_name='core/about.html'
   
    def get(self,request):
        return render(request,self.template_name,{})
    
    
class Term_And_Condition(View):
    template_name="core/terms-and-condition.html"
    def get (self,request):
        return render(request,self.template_name,{})
    
class Policy(View):
    template_name = "core/privacy_policy.html"
    def get (self,request):
        return render(request,self.template_name,{})
    
    
class PageNotFound(View):
    template_name = "shared/page_notfound.html"
    
    def get(self,request):
        return render(request,self.template_name,{})
    
    
class ServerError(View):
    template_name = 'shared/server_error.html'
    def get(self,request):
        return render(request,self.template_name)
    

@method_decorator(never_cache, name='dispatch')   
class AllProducts(LoginRequiredMixin,View):
    template_name= "core/all_products.html"
    login_url="login_user_url"
    def get(self,request):
        products = Product.objects.filter(is_deleted__isnull=False)
        page_number = request.GET.get('page')  # Use 'page' as the query parameter
        product_filter = Myfilter(request.GET,queryset=products)
        for fields in ['name','is_deleted']:
            del product_filter.form.fields[fields]
        paginator = Paginator(product_filter.qs, per_page=10)
        page_obj = paginator.get_page(page_number)  # Get the page object
     
        pricerange=products.aggregate(max_price=Max('price'),min_price=Min('price'))                  
        return render(request,self.template_name,{'products':product_filter.qs,'price_range':pricerange,'filter':product_filter,"pages":page_obj})
    

class Carrers(View):
    template_name='core/carrers.html'
    def get(self,request):
        return render(request,self.template_name)