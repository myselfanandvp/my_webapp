from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from users.models import AddressModel
from cart.models import Cart
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponseBadRequest
from profiles.models import Wallet
from .models import Order, OrderItem, ShippingAddress
from decimal import Decimal
from django.contrib import messages
import razorpay
from django.conf import settings
from django.db import transaction
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
import logging
from adminpanel.models import Transaction
from django.core.exceptions import ValidationError
from adminpanel.models import Coupon,CouponUsage

# Shipping address form view
@method_decorator(never_cache, name='dispatch')
class ShippingView(LoginRequiredMixin, View):
    login_url = "login_user_url"
    template_name = "checkout/shipping.html"

    def get(self, request):
        cart_items = Cart.objects.filter(user=request.user)
        addresses = AddressModel.objects.filter(user=request.user)
        if not cart_items.exists():
            messages.error(request, "There are no items in your cart for checkout!")
            return redirect('list_cart_url')
        coupons = Coupon.objects.filter(is_active=True)

        # Calculate totals
        original_total = sum(item.total_price for item in cart_items) + Decimal('50.00')
        applied_coupon = request.session.get('applied_coupon', None)
        
        if applied_coupon:
            final_total = Decimal(applied_coupon['discounted_total']) 
                      
        
        else:
            final_total = original_total


        wallet, created = Wallet.objects.get_or_create(user=request.user)

        # Create Razorpay client
        client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))

        # Create Razorpay order
        try:
            razorpay_order = client.order.create({
                "amount": int(final_total * 100),  # Amount in paise
                "currency": "INR",
                "payment_capture": 1
            })
        except Exception as e:
            messages.error(request, "Failed to initiate payment. Please try again.")
            return redirect('cart_url')

        return render(request, self.template_name, {
            'addresses': addresses,
            'cart_items': cart_items,
            'final_total': final_total,
            'wallet': wallet,
            'onlinepaymentamount': int(final_total * 100),
            'razorpayid': settings.RAZOR_KEY_ID,
            'name': "WaveLift",
            'order_id': razorpay_order["id"],
            'coupons':coupons,
        })

    def post(self, request):
        selected_address_id = request.POST.get('selected_address')
        applied_coupon = request.session.get('applied_coupon', None)
        
        if not selected_address_id:
            messages.error(request, "Please select a delivery address.")
            return redirect('shipping_url')

        original_address = get_object_or_404(AddressModel, user=request.user, id=selected_address_id)
        cart_items = Cart.objects.filter(user=request.user)
        if not cart_items.exists():
            messages.error(request, "Your cart is empty.")
            return redirect('cart_url')

        final_total = sum(item.total_price for item in cart_items) + Decimal('50.00')
        payment_method = request.POST.get('payment_method')
        
        if applied_coupon:
            discount_amount = Decimal(applied_coupon['discount_amount'])
            final_total = Decimal(applied_coupon['discounted_total'])
            
        

        if payment_method == "razorpay":
            # Re-create Razorpay order to ensure consistency
            client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
            try:
                payment_method = request.POST.get('payment_method')
        
                if applied_coupon:
                    discount_amount = Decimal(applied_coupon['discount_amount'])
                    final_total = Decimal(applied_coupon['discounted_total'])
                    
                razorpay_order = client.order.create({
                    "amount": int(final_total * 100),
                    "currency": "INR",
                    "payment_capture": 1
                })
            
            except Exception as e:
              
                messages.error(request, "Failed to initiate payment. Please try again.")
                return redirect('shipping_url')

            return render(request, self.template_name, {
                'addresses': AddressModel.objects.filter(user=request.user),
                'cart_items': cart_items,
                'final_total': final_total,
                'wallet': Wallet.objects.get_or_create(user=request.user)[0],
                'onlinepaymentamount': int(final_total * 100),
                'razorpayid': settings.RAZOR_KEY_ID,
                'name': "WaveLift",
                'order_id': razorpay_order["id"],
                'selected_address_id': selected_address_id,  # Pass selected address to template
            })

        # Create shipping address
        shipping_address = ShippingAddress.objects.create(
            full_name = original_address.full_name,
            type=original_address.type,
            alternate_phone_number=original_address.alternate_phone_number,
            street_address=original_address.street_address,
            city=original_address.city,
            state=original_address.state,
            postal_code=original_address.postal_code,
            country=original_address.country
        )

        try:
           
                if payment_method == "wallet":
                    wallet = get_object_or_404(Wallet, user=request.user)
                    if wallet.balance_amount < final_total:
                        messages.warning(request, "Your wallet balance is low to make this purchase!")
                        return redirect('shipping_url')
                    wallet.withdraw(final_total, "Order payment from wallet")

                    order = Order.objects.create(
                        user=request.user,
                        address=shipping_address,
                        payment_method=payment_method,
                        total_payment=final_total
                    )

                    for item in cart_items:
                        OrderItem.objects.create(
                            order=order,
                            product=item.product,
                            quantity=item.quantity,
                            price=item.product.price,
                            color=item.color,
                            total_price=item.total_price
                        )
                    cart_items.delete()
                    
                    if 'applied_coupon' in request.session:
                        try:
                            coupon_data = request.session['applied_coupon']
                            coupon = Coupon.objects.get(id=coupon_data['coupon_id'])
                            coupon_tran = coupon.apply_coupon(
                                user=request.user,
                                discount_amount=Decimal(coupon_data['discount_amount']))
                            
                            Transaction.objects.create(coupon_tran=coupon_tran,amount=final_total,user=request.user,wallet=wallet,payment_method="wallet",order=order,status=order.status)
                            request.session.pop('applied_coupon', None)
                            messages.success(request, "Order placed successfully!")
                            return redirect('confirmation')
                            
                        except Exception as e:
                            print (e)
                    else:
                        Transaction.objects.create(amount=final_total,user=request.user,wallet=wallet,payment_method="wallet",order=order,status=order.status)
                        messages.success(request, "Order placed successfully!")
                        return redirect('confirmation')                          

                elif payment_method == "cod":
                    order = Order.objects.create(
                        user=request.user,
                        address=shipping_address,
                        payment_method=payment_method,
                        total_payment=final_total
                    )

                    for item in cart_items:
                        OrderItem.objects.create(
                            order=order,
                            product=item.product,
                            quantity=item.quantity,
                            price=item.product.price,
                            color=item.color,
                            total_price=item.total_price
                        )
                    cart_items.delete()
                    
                    
                    if 'applied_coupon' in request.session:
                        try:
                            coupon_data = request.session['applied_coupon']
                            coupon = Coupon.objects.get(id=coupon_data['coupon_id'])
                            coupon_tran = coupon.apply_coupon(
                                user=request.user,
                                discount_amount=Decimal(coupon_data['discount_amount'])
                            )
                            Transaction.objects.create(
                                coupon_tran=coupon_tran,
                                amount=final_total,
                                user=request.user,
                                payment_method="cod",
                                order=order,
                                status=order.status
                            )
                            request.session.pop('applied_coupon', None)
                            
                            messages.success(request, "Order placed successfully!")
                            return redirect('confirmation')
                        
                        except Exception as e:
                            # optional logging or silent fail
                            print("Coupon application failed:", str(e))
                    else:
                        # Create transaction without coupon
                        Transaction.objects.create(
                            amount=final_total,
                            user=request.user,
                            payment_method="cod",
                            order=order,
                            status=order.status
                        )
                        
                        messages.success(request, "Order placed successfully!")
                        return redirect('confirmation')

                else:
                    messages.error(request, "Invalid payment method.")
                    return redirect('shipping_url')

        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            return redirect('shipping_url')

# Order success (confirmation) view
@method_decorator(never_cache, name='dispatch')
class OrderConfirmationView(LoginRequiredMixin, View):
    login_url = "login_user_url"
    template_name = 'orders/order_success.html'

    def get(self, request):
        return render(request, self.template_name)

# Order failed (confirmation) view
@method_decorator(never_cache, name='dispatch')
class OrderFailedView(LoginRequiredMixin, View):
    login_url = "login_user_url"
    template_name = 'orders/payment_failed.html'

    def get(self, request):
        return render(request, self.template_name)

@method_decorator(never_cache, name='dispatch')
class DiscountCoupon(LoginRequiredMixin, View):
    login_url = "login_user_url"
    def post(self, request):
   
        try:
            cart_products = Cart.objects.filter(user=request.user)
            total_amount = sum(item.total_price for item in cart_products) + Decimal('50.00')  # Including shipping
            coupon_code = request.POST.get('discount_coupon', '').strip()
            coupon = Coupon.objects.get(code__iexact=coupon_code, is_active=True)
            coupon_tran = CouponUsage.objects.filter(user = request.user,coupon=coupon).first()
            
            if  not coupon.is_valid():
                return JsonResponse({'status':"error","message":"This coupon is expired"})
        
            if coupon_tran:                
                if coupon_tran.usage_count>=coupon.max_uses_per_user:
                    return JsonResponse({"status":"error","message":"Your usage limit of this coupon is over"})
                
            
            if coupon.min_purchase>total_amount:
                return JsonResponse({"status":"error","message":f"Your total purchase amount should be upto {coupon.min_purchase} to apply this coupon"})
        
            
            if  request.session.get('applied_coupon'):
                return JsonResponse({"status":"error","message":"A coupon has already been applied."})
            
            
       
            coupon = Coupon.objects.get(code__iexact=coupon_code, is_active=True)
            discount_percentage = coupon.discount
            discount_amount = (discount_percentage / Decimal('100')) * total_amount
            discounted_total = total_amount - discount_amount
            

            # Store coupon details in session
            request.session['applied_coupon'] = {
                'coupon_id':str(coupon.id),
                'code': coupon.code,
                'discount_percentage': str(discount_percentage),
                'discount_amount': str(discount_amount),
                'discounted_total': str(discounted_total)              
            }

            return JsonResponse({
                "status": "success",
                "message": f"Coupon {coupon.code} applied successfully! {discount_percentage}% off",
                "code":str(coupon.code),
                "discount_per":str(coupon.discount),
                "original_total": str(total_amount),
                "discount_amount": str(discount_amount),
                "discounted_total": str(discounted_total),
            })
        except Coupon.DoesNotExist:
            # Clear any previously applied coupon
            request.session.pop('applied_coupon', None)
            return JsonResponse({
                "status": "error",
                "message": "The entered coupon is invalid or inactive."
            })
            
class RemoveCoupon(LoginRequiredMixin,View):
    def post(self,request):
        is_coupoun =  request.session.get('applied_coupon',None)
        if is_coupoun:
            request.session.pop('applied_coupon',None)
            messages.success(request,"Coupon has been removed")
        else:
            messages.error(request,"There is no coupon's applied")        
        return redirect('shipping_url')

@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(never_cache, name='dispatch')
class RazorpayPaymentHandlerView(LoginRequiredMixin, View):
    login_url = "login_user_url"

    def post(self, request):
        try:
            # Get Razorpay payment details from POST request
            applied_coupon = request.session.get('applied_coupon', None)
            payment_id = request.POST.get('razorpay_payment_id', '')
            razorpay_order_id = request.POST.get('razorpay_order_id', '')
            signature = request.POST.get('razorpay_signature', '')
            selected_address_id = request.POST.get('selected_address')

            if not all([payment_id, razorpay_order_id, signature, selected_address_id]):
                messages.error(request, "Incomplete payment data received.")
                return redirect('order_failed')

            # Verify payment signature
            client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }
            try:
                client.utility.verify_payment_signature(params_dict)
            except razorpay.errors.SignatureVerificationError as e:
                messages.error(request, "Payment verification failed. Please try again.")
                return redirect('order_failed')

            # Fetch cart items and address
            cart_items = Cart.objects.filter(user=request.user)
            if not cart_items.exists():
                messages.error(request, "Your cart is empty.")
                return redirect('cart_url')

            original_address = get_object_or_404(AddressModel, user=request.user, id=selected_address_id)
            final_total = sum(item.total_price for item in cart_items) + Decimal('50.00')
            if applied_coupon:
                final_total = Decimal(applied_coupon['discounted_total'])
                

            # Verify Razorpay order amount
            razorpay_order = client.order.fetch(razorpay_order_id)
            if razorpay_order['amount'] != int(final_total * 100):
                messages.error(request, "Payment amount mismatch.")
                return redirect('order_failed')

            # Create shipping address
            shipping_address = ShippingAddress.objects.create(
                type=original_address.type,
                full_name = original_address.full_name,
                alternate_phone_number=original_address.alternate_phone_number,
                street_address=original_address.street_address,
                city=original_address.city,
                state=original_address.state,
                postal_code=original_address.postal_code,
                country=original_address.country
            )
            

            # Create order and order items
            with transaction.atomic():
                order = Order.objects.create(
                    user=request.user,
                    address=shipping_address,
                    payment_method='razorpay',
                    total_payment=final_total,
                    razorpay_order_id=razorpay_order_id,
                    razorpay_payment_id=payment_id,
                    razorpay_signature=signature
                )

                for item in cart_items:
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        quantity=item.quantity,
                        price=item.product.price,
                        color=item.color,
                        total_price=item.total_price
                    )
             
                cart_items.delete()                
                if 'applied_coupon' in request.session:
                        try:
                            coupon_data = request.session['applied_coupon']
                            coupon = Coupon.objects.get(id=coupon_data['coupon_id'])
                            coupon_tran = coupon.apply_coupon(
                                user=request.user,
                                discount_amount=Decimal(coupon_data['discount_amount'])
                            )
                            Transaction.objects.create(coupon_tran=coupon_tran,user=request.user,payment_method="razorpay",order=order,status=order.status,gateway_transaction_id=payment_id,reference_id=razorpay_order_id,amount=final_total)
                            request.session.pop('applied_coupon', None)
                            messages.success(request, "Payment successful! Your order has been placed.")     
                            return redirect('confirmation')
                        except Exception as e:
                            print(e)                            
                else:
                    Transaction.objects.create(user=request.user,payment_method="razorpay",order=order,status=order.status,gateway_transaction_id=payment_id,reference_id=razorpay_order_id,amount=final_total)
                    messages.success(request, "Payment successful! Your order has been placed.")     
                    return redirect('confirmation')

        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            return redirect('order_failed')
        
        
        
class AddNewAddress(View):
    
    def post(self, request):
        try:
            address = AddressModel()  # Create instance
            message = address.addaddress(
                full_name = request.POST.get('full_name',''),
                address_type=request.POST.get('address_type','Home'),
                alternate_phone_number=request.POST.get('phone', ''),  # Match form field name
                street_address=request.POST.get('street', ''),  # Match form field name
                city=request.POST.get('city', ''),
                state=request.POST.get('state', ''),
                postal_code=request.POST.get('postal_code', ''),
                country=request.POST.get('country', ''),
                user=request.user
            )
        
            return JsonResponse(message, status=201)
            
        except Exception as e:      
            return JsonResponse({"status":"error","message": str(e)}, status=400)
        
        

