from django.db import models
from uuid import uuid4

# Create your models here.
from django.core.validators import MinValueValidator
from users.models import User, AddressModel
from products.models import Product,ProductColor
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from django.http import JsonResponse
from django.utils import timezone

class ShippingAddress(models.Model):
    id = models.UUIDField(verbose_name="ID", primary_key=True, default=uuid4)
    full_name = models.CharField(verbose_name="Full Name", max_length=100,blank=True,null=True)
    type = models.CharField(verbose_name="Type", max_length=100,default="Home")
    alternate_phone_number = models.CharField(verbose_name="Alternate Phone Number", max_length=10, validators=[RegexValidator(regex=r'\d{10}$',message="Phone number must be exactly 10 digits (e.g., 9847525210)")])
    street_address = models.CharField(
        verbose_name="Street Address", max_length=250)
    city = models.CharField(verbose_name="City", max_length=100)
    state = models.CharField(verbose_name="State/Province", max_length=100)
    postal_code = models.CharField(verbose_name="Postal Code", max_length=6)
    country = models.CharField(verbose_name="Country", max_length=100)
    created_at = models.DateTimeField(
        verbose_name="Created At", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="Updated At", auto_now=True)
   
    class Meta:
        verbose_name = "ShippingAddress"

    def __str__(self):
        return f"{self.type} - {self.street_address}, {self.city}"
    
        
        
            
class Order(models.Model):
    id = models.UUIDField(primary_key=True, verbose_name="ID",
                          default=uuid4, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='order_user')
    address = models.ForeignKey(
        ShippingAddress, on_delete=models.CASCADE, null=True, related_name='order_address')
    payment_method = models.CharField(max_length=50)
    total_payment = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=50, choices=[
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('canceled', 'Canceled'),
        ('return', 'Return'),
    ], default='pending')
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=200, blank=True, null=True)
    
    cancellation_reason = models.CharField(verbose_name= "Reason",blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "orders"
        ordering = ['-created_at']

    def __str__(self):
        return f"Order {self.id} by {self.user.username} orderamount: {self.total_payment} order_status: {self.status}"


class OrderItem(models.Model):
    id = models.UUIDField(primary_key=True, verbose_name="ID",
                          default=uuid4, editable=False)
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE,related_name='order_products')
    color= models.ForeignKey(ProductColor,on_delete=models.SET_NULL,related_name="item_color",blank=True,null=True)
    quantity = models.PositiveIntegerField()
    status= models.CharField(max_length=100,blank=True,null=True)
    return_reason = models.CharField(max_length=100,blank=True,null=True)
    # snapshot of price at order time
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now=True,null=True)
    updated_at = models.DateTimeField(auto_now_add=True,null=True)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} (₹{self.price})"
    
    def order_return(self,reason):
        if self.status=="Return":
            raise ValueError("The product is already in the return stage")
        self.return_reason = reason
        self.status = "Return"
        self.save()
        
    @property
    def get_product_price(self):
        return self.price
        
    def order_return_accept(self):
        if self.status=='Return':
            self.status = "Returned"
            self.save()
            
    @property  
    def product_name(self):
        return self.product.name
      

    class Meta:
        db_table = "orderitems"
        
        
