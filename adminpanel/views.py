from django.shortcuts import render,redirect,get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin,UserPassesTestMixin
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from users.models import User
from products.models import Product
from .models import Transaction,Coupon
from .filters import User,UserFilter,OrderFilter
from django.core.paginator import Paginator
from checkout.models import Order,AddressModel,OrderItem
from django.contrib import messages
from django.http import HttpResponse,JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .forms import CouponForm
from django.utils import timezone
from django.utils.timezone import timedelta
from django.db.models.aggregates import Avg,Max,Min,Sum
from django.template.loader import render_to_string
from weasyprint import HTML
from profiles.models import Wallet,WalletTransaction
from django.views.decorators.csrf import csrf_exempt
from django.db.models.functions import ExtractWeek,ExtractMonth,ExtractYear,TruncDate
from django.db.models import Q 
from users.models import ReferralRelationship
from datetime import datetime


# Create your views here.

@method_decorator(never_cache, name='dispatch')
class AdminDashboard(LoginRequiredMixin,UserPassesTestMixin,View):
    login_url='login_admin_url'
    user_url = 'login_user_url'
    template_name = 'admin/admin_dashboard.html'
    summary_card = 'cotton/admin_summary_card.html'
    
    def test_func(self):
        return self.request.user.is_superuser
    
    def handle_no_permission(self):
        return redirect(self.user_url)
    
    def get(self,request):
        users = User.objects.filter(is_superuser=False).count()
        total_tran_amount = Transaction.objects.aggregate(Sum('amount'))['amount__sum'] or 0
        total_products = Product.objects.all().count()
        orders = Order.objects.all()
        orders_count= orders.count()
        pending_count=orders.filter(status__icontains='pending').count()
        canceled_count = orders.filter(status__icontains='canceled').count()
        shipped_count = orders.filter(status__icontains='shipped').count()        
        delivered_count= orders.filter(status__icontains='delivered').count()
        returned_items_count = OrderItem.objects.filter(status = 'Returned').count()
        return_items_count = OrderItem.objects.filter(status = 'Return').count()
        
        print(return_items_count)
        
   
        top_products = (
                OrderItem.objects
                .filter(order__status='delivered')
                .values('product__id', 'product__name')
                .annotate(total_sold=Sum('quantity'))
                .order_by('-total_sold')[:10]
            )
        
        top_categories = (
            OrderItem.objects
            .filter(order__status='delivered')   # only completed sales
            .values('product__category__id', 'product__category__name')
            .annotate(total_sold=Sum('quantity'))
            .order_by('-total_sold')[:10]
        )
        
        top_brands = (OrderItem.objects.filter(order__status='delivered')
                     .values('product__brand__name')).annotate(total_sold=Sum('quantity')).order_by('-total_sold')[:10]

       

        if request.headers.get("HX-Request"):
            return render(request,self.summary_card,{"total_tran_amount":total_tran_amount,'total_users':users,'order_count':orders_count,'pending_count':pending_count,'delivered_count':delivered_count,'canceled_count':canceled_count,'shipped_count':shipped_count,'product_count':total_products,'return_items_count':return_items_count,'returned_items_count':returned_items_count})        
        return render(request,self.template_name,{"total_tran_amount":total_tran_amount,'total_users':users,'order_count':orders_count,'pending_count':pending_count,'delivered_count':delivered_count,'canceled_count':canceled_count,'shipped_count':shipped_count,
                                                  'product_count':total_products,'top_products':top_products,'top_categories':top_categories,'top_brands':top_brands,'return_items_count':return_items_count,'returned_items_count':returned_items_count})
    
    

@method_decorator(never_cache, name='dispatch')
class ListUser(LoginRequiredMixin,View):
    login_url='login_admin_url'
    template_name = "admin/user_list.html"
    def get(self,request):
        
        my_users= User.objects.exclude(is_superuser=1).order_by('-created_at').values('email','phone_number','is_active','username','id',"created_at")
        user_filter=UserFilter(request.GET,queryset=my_users)
        page_number = request.GET.get('page')  # Use 'page' as the query parameter
        paginator = Paginator(user_filter.qs, per_page=3)
        page_obj = paginator.get_page(page_number)  # Get the page object
     
        return render(request,self.template_name,{"users":user_filter.qs,'myFilter':user_filter,'pages':page_obj})

@method_decorator(never_cache, name='dispatch')
class UserDetails(LoginRequiredMixin,View):
    template_name="admin/customer_details.html"
    def get(self,request,id):
        user = User.objects.get(id=id)
        trans =Transaction.objects.filter(user=user)
        total_trans_amount=sum([i.amount for i in trans])
        print(total_trans_amount)
        return render(request,self.template_name,{'user':user,'total_trans_amount':total_trans_amount})
    
    

@method_decorator(never_cache, name='dispatch')
class OrderList(LoginRequiredMixin,View):
    login_url='login_admin_url'
    
    template_name = "admin/orders.html"
    
    def get(self,request):
        orders =Order.objects.all()
        filter= OrderFilter(request.GET,queryset=orders)
        page_number = request.GET.get('page')
        paginator = Paginator(filter.qs,per_page=10)
        page_obj=paginator.get_page(page_number)
        
        return render(request,self.template_name,{'orders':page_obj,'filter':filter})
   

@method_decorator(never_cache, name='dispatch') 
class OrderDetails(LoginRequiredMixin,View):
    login_url="login_admin_url"
    template_name = "admin/order_details.html"
    def get(self,request):        
        orderid=request.GET.get('orderid')
        order = get_object_or_404(Order,id=orderid)      
        return render(request,self.template_name,{'order':order})
    
    
    def post(self,request):
        status = request.POST.get('status')
        orderid = request.POST.get('orderid')   
        
        order = get_object_or_404(Order,id=orderid)
        
        if order.status=="pending" and status in ('pending','confirmed'):
            messages.error(request,f"Cannot update {status}")
            return redirect('order_list_url')
        
        if order.status=="confirmed" and status in ('confirmed'):
            messages.error(request,f"Cannot update {status}")
            return redirect('order_list_url')
                
        if order.status == 'delivered' and status in ('canceled','pending','shipped','confirmed','delivered'):
            messages.error(request, f"Cannot update {status} a delivered order.")
            return redirect('order_list_url')
        
        if order.status == 'shipped' and status in ('canceled','pending','shipped','confirmed'):
            messages.error(request, f"Cannot update {status} a shipped order.")
            return redirect('order_list_url')
        
        if order.status=="return" and status in ('canceled','pending','shipped','confirmed','delivered'):
            messages.error(request,"This product is in the return stage")
            return redirect('order_list_url')
        
        if  order.status == 'canceled' and status in ('canceled','pending','shipped','confirmed',"delivered"):
            messages.warning(request, "Order is already canceled!")
            return redirect('order_list_url')
        
           
        order.status=status        
        order.save()        
        messages.success(request,"Status was changed") 
        return redirect('order_list_url')
  
  

@method_decorator(never_cache,name='dispatch')
class CouponView(LoginRequiredMixin,View):
    login_url="login_admin_url"
    template_name= "admin/coupon.html"
    def get(self,request):
        form = CouponForm()
        coupons = Coupon.objects.all()
        return render(request,self.template_name,{'form':form,'coupons':coupons})
    
    def post(self,request):
        form = CouponForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"Coupon created successfully")
            return redirect('coupon_url')
        messages.error(request,'Coupon creation failed')
        coupons = Coupon.objects.all()
        return render(request,self.template_name,{'form':form,'coupons':coupons})
        
        
            
    
@method_decorator(csrf_exempt,name='dispatch')  
class DeleteCoupons(View):
    def post (self,request,id): 
        Coupon.objects.get(id=id).delete()
        messages.success(request,"Coupon delete successfully")     
        return redirect('coupon_url')
    
    
    
    
@method_decorator(csrf_exempt, name='dispatch')
class SaleReport(View):
    template_name = 'admin/sales_report.html'

    def get(self, request):
        transactions = Transaction.objects.all().order_by('-created_at')
        discount_amount = transactions.aggregate(discount_total=Sum('coupon_tran__discount_amount'))['discount_total']
        total_amount = transactions.aggregate(total=Sum('amount'))['total']
        return render(request, self.template_name, {'transactions': transactions,'total_amount':total_amount,'discount_amount': discount_amount,})

    def post(self, request):
        today = timezone.now()
        transactions = Transaction.objects.all().order_by('-created_at')

        def tranfilter(argument):
            match argument:
                case 'daily':
                    start_day = today.replace(hour=0, minute=0, second=0, microsecond=0)
                    return transactions.filter(created_at__gte=start_day)
                case 'weekly':
                    start_week = today - timedelta(days=today.weekday())  # Monday of this week
                    return transactions.filter(created_at__gte=start_week)
                case 'monthly':
                    return transactions.filter(created_at__year=today.year, created_at__month=today.month)
                case 'yearly':
                    return transactions.filter(created_at__year=today.year)
                case 'custom':
                    start_date = request.POST.get('from_date')
                    end_date = request.POST.get('to_date')
                    if start_date and end_date:
                        try:
                            return transactions.filter(created_at__range=(start_date, end_date)).order_by('-created_at')
                        except ValueError:
                            messages.error(request, "Please provide valid dates")
                            return transactions
                    messages.error(request, "Please provide both start and end dates")
                    return transactions
                case _:
                    return transactions

        period = request.POST.get('period')
        filtered_transactions = tranfilter(period) if period else transactions
        total_amount = filtered_transactions.aggregate(total_amount=Sum('amount'))['total_amount'] or 0
        discount_amount = filtered_transactions.aggregate(discount_total=Sum('coupon_tran__discount_amount'))['discount_total'] or 0

        if request.POST.get('format') == 'pdf':
            # Render the HTML template for WeasyPrint
            html_string = render_to_string('admin/sales_report_pdf.html', {
                'transactions': filtered_transactions,
                'total_amount': total_amount,
                'discount_amount': discount_amount,
                'period': period or 'all',
                'from_date': request.POST.get('from_date'),
                'to_date': request.POST.get('to_date'),
                'generated_date':request.POST.get('present_date'),
            })
    
            # Generate PDF
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="transaction_report_{today.date()}.pdf"'
            HTML(string=html_string).write_pdf(response)
            return response

        return render(request, self.template_name, {
            'transactions': filtered_transactions,
            'total_amount': total_amount,
            'discount_amount': discount_amount,
            'period': period,
            'generated_date':today.date(),
        })
        
        
        
    
@method_decorator(csrf_exempt ,name='dispatch')
class ActivateCoupon(View):
    def post(self,request):       
        coupon_id = request.POST.get('coupon_id',None)
        coupon = Coupon.objects.filter(id=coupon_id).first()
        coupon.activate()  
        messages.success(request,"Coupon is activated") 
        return redirect('coupon_url')    
    
    
@method_decorator(csrf_exempt,name="dispatch")
class DeactivateCoupon(View):
    def post(self,request):
        coupon_id = request.POST.get('coupon_id',None)
        coupon = Coupon.objects.filter(id=coupon_id).first()
        if coupon:
            coupon.deactivate()  
            messages.success(request,"Coupon is deactivated!") 
            return redirect('coupon_url')    
        messages.error(request,'Something went wrong')
        return redirect('coupon_url')
    
    
class GeneratePDF(View):
    template_name = "admin/sales_report_pdf.html"
    def get(self,request):
        return render(request,self.template_name,{})
    
    
class ListTransctions(View):
    template_name ='admin/all_transcations.html'
    partial_view = 'cotton/whole_tran.html'
    def get(self,request):
        transactions = Transaction.objects.all()
        tran_filter = request.GET.get('filter',None)
        clear_filter = request.GET.get('clearfilter',None)
        if tran_filter=='datafilter':
            tran_type = request.GET.get('type',None)
            date_from = request.GET.get('date_from',None)
            date_to = request.GET.get('date_to',None)
            status_type = request.GET.get('status',None)
            
            if tran_type and date_from and date_to and status_type:
                filtered_data = transactions.filter(created_at__date__range=(date_from,date_to),payment_method__icontains=tran_type,order__status__icontains=status_type)
                
            elif tran_type and date_from and date_to:
                filtered_data = transactions.filter(created_at__date__range=(date_from,date_to),payment_method__icontains=tran_type)
            
            elif status_type and date_from and date_to:
                filtered_data = transactions.filter(created_at__date__range=(date_from,date_to),order__status__icontains=status_type)
                                
            elif status_type and tran_type:
                filtered_data = transactions.filter(order__status__icontains= status_type,payment_method=tran_type) 
            elif tran_type:
                filtered_data = transactions.filter(payment_method__icontains=tran_type)
            elif date_from and date_to:
                filtered_data = transactions.filter(created_at__date__range=(date_from,date_to)) 
            elif status_type:
                filtered_data = transactions.filter(order__status__icontains= status_type)                   
            else:
                filtered_data=transactions
            return render(request,self.partial_view,{'transactions':filtered_data})
        
        elif clear_filter=='resetdata': 
            
            return render(request,self.partial_view,{'transactions':transactions})
        
        return render(request,self.template_name,{'transactions':transactions})
    

        
    
    
class TranscationDetails(View):
    template_name = 'admin/transcation_detail.html'
    def get(self,request,tranid):
        print(tranid)
        transaction = Transaction.objects.filter(id=tranid).first()
     
        return render(request,self.template_name,{'transaction':transaction})
    
    
class AdminOrderDetail(View):
    template_name = 'admin/order_detail.html'
    
    def get(self,request,order_id):
        order = Order.objects.filter(id=order_id)       
        return render(request,self.template_name,{'orders':order})
    
    
    
@method_decorator(csrf_exempt,name='dispatch')
class AdminWalletTranscations(View):
    template_name = 'admin/wallet_transcations.html'
    def get(self,request):
        if request.GET.get('data',None):
            wallet = Wallet.objects.filter(user__is_superuser=False)
            return render(request,'cotton/wallet_tran_list.html',{'wallet':wallet})
        wallet = Wallet.objects.filter(user__is_superuser=False)
        return render(request,self.template_name ,{'wallet':wallet})
    
    def post(self,request):
      
        date_from = request.POST.get('date_from',None)
        date_to = request.POST.get('date_to',None)
        user_name = request.POST.get('username',None)
       

        if user_name and date_from and date_to:
            wallet = Wallet.objects.filter(user__username__icontains=user_name,created_at__date__range=(date_from,date_to))
              
        elif  date_from and date_to:     
            wallet = Wallet.objects.filter(user__is_superuser=False,created_at__date__range=(date_from,date_to))
        elif user_name:
            wallet = Wallet.objects.filter(user__is_superuser=False,user__username__icontains=user_name)
            
        else:
            wallet = Wallet.objects.filter(user__is_superuser=False)
            
        return render(request,'cotton/wallet_tran_list.html',{'wallet':wallet})
    
    
@method_decorator(csrf_exempt,name='dispatch')
class AdminWalletDetails(LoginRequiredMixin,View):
    template_name = 'admin/wallet_tran_detail.html'
    partial_view = 'cotton/wallet_tran_details.html'
    def get(self,request,wallet_id):
        wallet_transcations = WalletTransaction.objects.filter(wallet__id= wallet_id)
        balance =wallet_transcations.first().balance_amounts
        wallet_id = wallet_transcations.first().wallet.id
        clearfilter = request.GET.get('clearfilter',None)
        if clearfilter:
            print(clearfilter)
            return render(request,self.partial_view,{'wallet_transcations':wallet_transcations})
        else:        
            return render(request,self.template_name,{'wallet_transcations':wallet_transcations,'wallet_balance':balance,'wallet_id':wallet_id})
    
    def post(self,request,wallet_id):
        
        tran_type= request.POST.get('tran_type',None)
        date_from = request.POST.get('date_from',None)
        date_to = request.POST.get('date_to',None)
        wallet_transcations = WalletTransaction.objects.filter(wallet__id=wallet_id)
        
        if date_from and date_to and tran_type:
            filter_data = wallet_transcations.filter(created_at__date__range=(date_from,date_to),transaction_type__icontains=tran_type)
            
        elif date_from and date_to:
            filter_data = wallet_transcations.filter(created_at__date__range=(date_from,date_to))
            
        elif tran_type:
            filter_data = wallet_transcations.filter(transaction_type__icontains=tran_type)
            
        else:
            filter_data = wallet_transcations
        
     
        return render(request,self.partial_view,{'wallet_transcations':filter_data})
    
@method_decorator(csrf_exempt,name='dispatch')
class ChartView(LoginRequiredMixin,View):
    def post(self,request):  
        filter_type = request.POST.get('filter',None)  
        if filter_type == "yearly":
            qs = (
                Order.objects.annotate(year=ExtractYear("created_at"))
                .values("year")
                .annotate(total_sales=Sum("total_payment"))
                .order_by("year")
            )
            data = list(qs)

        elif filter_type == "monthly":
            qs = (
                Order.objects.annotate(month=ExtractMonth("created_at"))
                .values("month")
                .annotate(total_sales=Sum("total_payment"))
                .order_by("month")
            )
            data = list(qs)

        elif filter_type == "weekly":
            qs = (
                Order.objects.annotate(week=ExtractWeek("created_at"))
                .values("week")
                .annotate(total_sales=Sum("total_payment"))
                .order_by("week")
            )
            data = list(qs)

        elif filter_type == "daily":
            qs = (
                Order.objects.annotate(day=TruncDate("created_at"))
                .values("day")
                .annotate(total_sales=Sum("total_payment"))
                .order_by("day")
            )
            data = list(qs)

        else:
            return JsonResponse({"error": "Invalid filter type"}, status=400)

        return JsonResponse({"filter": filter_type, "results": data}, safe=False)
    
    
    
class Refferals(View):
    template_name ='admin/refferals.html'
    def get(self,request):
        referrals = ReferralRelationship.objects.all()
        total_referred_amount= WalletTransaction.objects.filter(transaction_type ='referral').aggregate(Sum('amount')).get('amount__sum',0)
        total_welcome_amount= WalletTransaction.objects.filter(transaction_type ='welcome').aggregate(Sum('amount')).get('amount__sum',0)
        return render(request,self.template_name,{'referrals':referrals,'total_referred_amount':total_referred_amount,'total_welcome_amount':total_welcome_amount})
    
    def post(self,request):
        pass

      
class OrderReturnAccept(View):
    template_name = 'cotton/return_action.html'
    def post(self,request): 
        item_id= request.POST.get('itemid')    
        wallet_id= request.POST.get('wallet_id')    
        item = get_object_or_404(OrderItem,id= item_id)
        wallet =get_object_or_404(Wallet,id=wallet_id)
        return_amount = item.get_product_price
        wallet.deposit(amount=return_amount, description="Refund credited for returned product.",transaction_type='refund')
        item.order_return_accept()
        return render(request,self.template_name,{"item": item})
    
    
class ReturnItems(View):
    template_name='admin/return_items.html'    
    partial_template_name = 'cotton/return_items_list.html'
    def get(self,request):
        return_items = OrderItem.objects.filter(Q(status='Return') | Q(status='Returned'))
        
        if request.headers.get('Hx-Request'): 
            print(request.GET) 
            status = request.GET.get('status')
            item_id = request.GET.get('item_id')
            if status:                
                filter_items = return_items.filter(status=status) 
            elif item_id:
                item_id = str(item_id).replace('\t','').strip()
                filter_items = return_items.filter(id=item_id) 
            else:     
                filter_items = return_items     
            return render(request,self.partial_template_name,{'return_items':filter_items})
       
        return render(request,self.template_name,{'return_items':return_items})
    
 
    

       
    

        
    
    

        
    