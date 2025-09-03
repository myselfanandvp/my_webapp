from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Coupon

@receiver(pre_save,sender=Coupon)
def deactivate_expired_coupon(sender,instance,**kwargs):
    if not instance.is_valid():
        instance.is_active=False
        
