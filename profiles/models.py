from django.db import models
from uuid import uuid4
from users.models import User
from decimal import Decimal
from django.utils import timezone
from datetime import datetime


class Wallet(models.Model):
    id = models.UUIDField(verbose_name="ID",primary_key=True,default=uuid4)
    balance = models.DecimalField(
    max_digits=12,       # total digits (including decimals)
    decimal_places=2,    # 2 decimal places like 0.00
    default=Decimal("0.00")
)
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name="wallet")
  
    created_at= models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table="wallet"
    
    def __str__(self):
        return f"{self.user.first_name}'s Wallet - ₹{self.balance:.2f}"

    
    @property
    def balance_amount(self):
        return self.balance
    
  
    def deposit(self,amount, description="",transaction_type='deposit',razorpay_order_id=None,razorpay_payment_id=None,razorpay_signature=None):
        if amount <= 0:
            raise ValueError("Deposit amount must be positive.")
        self.balance+=amount
        self.save()
        WalletTransaction.objects.create(wallet=self,transaction_type=transaction_type,
                                         amount=amount,description=description,
                                         razorpay_order_id=razorpay_order_id
                                      ,razorpay_payment_id=razorpay_payment_id,razorpay_signature=razorpay_signature                                 
                                         )
        
    def withdraw(self,amount,description="",transaction_type='withdrawal'):
        if amount<=0:
            raise ValueError("Withdrawal amount must be positive.")
        if self.balance < amount:
            raise ValueError("Insufficient balance.")
        self.balance-=amount
        self.save()
        WalletTransaction.objects.create(wallet=self,transaction_type=transaction_type,amount=amount,description=description)
            
        
    
    
    
class WalletTransaction(models.Model):
    TRANSACTION_TYPES = [
        ("deposit", "Deposit"),
        ("withdrawal", "Withdrawal"),
        ("refund", "Refund"),
        ("referral", "Referral Bonus"),   
        ("welcome", "Welcome Bonus"),    
    ]

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name="transactions")
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
      
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=200, blank=True, null=True)
    
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "wallet_transaction"
        ordering = ["-created_at"]
        
    

    def __str__(self):
        return f"{self.transaction_type.title()} of ₹{self.amount:.2f}"
    
    @property
    def balance_amounts(self):
       return self.wallet.balance
   
    @property
    def referral_amount(self):
        return self.amount if self.transaction_type == 'referral' else 0
        
    @property
    def welcome_amount(self):
        return self.amount if self.transaction_type=='welcome' else 0
            