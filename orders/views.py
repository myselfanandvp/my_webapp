from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from checkout.models import Order,OrderItem
from django.views import View
from django.contrib import messages
from products.models import Product
from django.http import HttpResponse,JsonResponse
from django.template.loader import render_to_string
from weasyprint import HTML
import os
from profiles.models import Wallet
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
# Create your views here.


# Review & place order view
from django.db import transaction

class OrderReviewView(LoginRequiredMixin, View):
    login_url = "login_user_url"
    template_name = 'orders/orders.html'

    def get(self, request):
        orders = Order.objects.filter(user=request.user)
        if not orders.exists():
            messages.info(request, "You have no orders to display.")
        return render(request, self.template_name, {'orders': orders})

    def post(self, request):
        order_id = request.POST.get("order_id")
        reason = request.POST.get("cancellation_reason", "").strip()

        try:
            order = Order.objects.get(id=order_id, user=request.user)

            # Normalize status for comparison
            if order.status.lower() not in ["pending", "processing"]:
                messages.error(request, f"Order #{order.id} cannot be canceled.")
                return redirect("orders_url")

            # Prevent double cancellation
            if order.status.lower() == "canceled":
                messages.warning(request, f"Order #{order.id} is already canceled.")
                return redirect("orders_url")

            with transaction.atomic():
                # Restock items
                order_items = OrderItem.objects.filter(order=order)
                for item in order_items:
                    item.product.stock_qty += item.quantity
                    item.product.save()

                # Update status & reason
                order.status = "canceled"
                order.cancellation_reason = reason
                order.save()

                # Refund if wallet or razorpay payment
                if order.payment_method in ("wallet",'razorpay'):
                    wallet = get_object_or_404(Wallet, user=request.user)
                    wallet.deposit(
                        order.total_payment,
                        description="Order cancelled - money credited"
                    )
        

            messages.success(request, f"Order #{order.id} has been canceled and refunded if applicable.")

        except Order.DoesNotExist:
            messages.error(request, "Order not found.")
        except Exception as e:
            messages.error(request, f"An unexpected error occurred: {str(e)}")

        return redirect("orders_url")

    
class OrderDetail(View):
    template_name = "orders/orderdetails.html"
    def post(self,request):
        order_id = request.POST.get('orderid')
        orders = Order.objects.filter(user=request.user,id = order_id)
        return render(request,self.template_name,{'orders':orders})
    
    
    

class GeneratePDF(View):
    template_name = "orders/orderdetails.html"
    def post(self,request):
        order_id = request.POST.get('orderid','')
        order = get_object_or_404(Order,id=order_id,user= request.user)
        # Render the LaTeX template as HTML for WeasyPrint
        html_string = render_to_string('orders/order_details_pdf.html', {'order': order,'time':timezone.now})
        #Generate PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="order_{order.id}.pdf"'
        HTML(string=html_string).write_pdf(response)
        return response
    
@method_decorator(csrf_exempt,name='dispatch')
class OrderReturn(View): 
    def post(self,request):
        reason = json.loads(request.body)['reason']
        id = json.loads(request.body)['itemid']
        orderitem = get_object_or_404(OrderItem,id=id)
        try:
            orderitem.order_return(reason)          
            return JsonResponse({"status": "success", "message": "Order return initiated"})
        except ValueError as e:
            return JsonResponse({"status": "error", "message": f"{str(e)}"})
        
        

            
            