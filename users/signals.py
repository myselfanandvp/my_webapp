import string
import secrets
from django.db.models.signals import pre_save,post_save
from django.dispatch import receiver
from .models import User,ReferralRelationship
from profiles.models import Wallet
from decimal import Decimal




def generate_referral_code(length=10):
    characters = string.ascii_uppercase+ string.digits
    return ''.join(secrets.choice(characters)for _ in range(length))


@receiver(pre_save,sender=User)
def add_referral_code(sender,instance,**kwargs):
    if not instance.referral_code:
        instance.referral_code = generate_referral_code()
        
        

@receiver(post_save, sender=User)
def create_user_wallet(sender, instance, created, **kwargs):
    if created and not hasattr(instance, "wallet"):
        Wallet.objects.create(user=instance) 
        


        
@receiver(post_save,sender=User)
def create_referral_realationship(sender,instance,created,**kwargs):
    if created:
        referral_code = getattr(instance, "_signup_referral_code", None)
        if referral_code:
            try:
                referrer = User.objects.get(referral_code=referral_code)
                ReferralRelationship.objects.get_or_create(
                    referrer=referrer,
                    referred=instance
                )
                
                referrer.wallet.deposit(
                    Decimal("1000.00"),
                    description=f"Referral bonus for inviting {instance.email}",
                    transaction_type='referral'
                )
                
                instance.wallet.deposit(
                    Decimal("500.00"),
                    description=f"Welcome bonus for using referral code {referrer.referral_code}",
                    transaction_type='welcome'
                )
                 
                 
            except User.DoesNotExist:
                pass