

# Create your models here.


from django.db import models
from uuid import uuid4
from decimal import Decimal
from users.models import User
from checkout.models import Order
from profiles.models import   Wallet # optional
from django.core.validators import MinValueValidator,MaxValueValidator
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db import IntegrityError


class Coupon(models.Model):
    
    id   = models.UUIDField(default=uuid4,primary_key=True,editable=False)
    
    code = models.CharField(
        max_length=50,
        unique=True,
        help_text="Unique coupon code (e.g., SAVE20)",
    )
    discount = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0.01), MaxValueValidator(100.00)],
        help_text="Discount percentage (1.00 to 100.00)",
    )
    
    expiry_date = models.DateField(
        help_text="Date when the coupon expires",
    )
    max_uses_per_user = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text="Maximum number of times a single user can use this coupon",
    )
    is_active = models.BooleanField(default=True)
    
    min_purchase = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.00)],
        help_text="Minimum purchase amount required to apply the coupon",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the coupon was created",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the coupon was last updated",
    )

    class Meta:
        db_table='coupons'
        ordering = ['-created_at']
        verbose_name = "Coupon"
        verbose_name_plural = "Coupons"

    def __str__(self):
        return f"{self.code} ({self.discount}% off)"

    def is_valid(self):
        """Check if the coupon is still valid based on expiry date."""
        return self.expiry_date >= timezone.now().date()
    
    
    def activate(self):
        self.is_active=True
        self.save()
        

    def deactivate(self):
        self.is_active=False
        self.save()
    
    def apply_coupon(self,user,discount_amount):
      usage, created= CouponUsage.objects.get_or_create(coupon=self,user=user)
      if usage.usage_count<self.max_uses_per_user:
          usage.discount_amount+=discount_amount
          usage.usage_count +=1
          usage.save()
          return usage
      return created
    
    
    
    
    
   

class CouponUsage(models.Model):
    id = models.UUIDField(default=uuid4,primary_key=True,editable=False)
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='user_coupon')
    coupon = models.ForeignKey(Coupon,on_delete=models.CASCADE,related_name='coupons')
    usage_count = models.IntegerField(default=0)
    discount_amount= models.IntegerField(default=0)
    
    class Meta:
        db_table = 'coupon_transcations'   
        
        
     
        

class Transaction(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('wallet', 'Wallet'),
        ('razorpay', 'Razorpay'),
        ('cod', 'Cash on Delivery'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='all_transactions')
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')
    wallet = models.ForeignKey(Wallet, on_delete=models.SET_NULL, null=True, blank=True,related_name='wallet_transcations')
    coupon_tran= models.ForeignKey(CouponUsage,on_delete=models.SET_NULL,null=True,blank=True,related_name='coupon_transcations')

    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    amount = models.DecimalField(max_digits=12, decimal_places=2)
   
    currency = models.CharField(max_length=10, default='INR')

    # For Razorpay or other gateways
    gateway_transaction_id = models.CharField(max_length=100, blank=True, null=True)
    reference_id = models.CharField(max_length=100, blank=True, null=True)  # optional internal reference

    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "all_transactions"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.email} - ₹{self.amount} via {self.payment_method.upper()}"
    

    