from uuid import uuid4
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from cloudinary.models import CloudinaryField
from django.utils import timezone

class User(AbstractUser, PermissionsMixin):

    id = models.UUIDField(_('User ID'), default=uuid4,
                          primary_key=True, editable=False)
    username = models.CharField(
        _('User Name'), max_length=150,unique=True, null=True, blank=True, default=None)
    email = models.EmailField(
        _('Email Address'), unique=True, blank=False, null=False)

    phone_number = models.CharField(
        max_length=10,
        unique=True,
        null=True,
        blank=False,
        validators=[
            RegexValidator(
                regex=r'\d{10}$',
                message="Phone number must be exactly 10 digits (e.g., 9847525210)"
            )
        ]
    )

    # profile_img = models.ImageField(
    #     upload_to='profile_images/', blank=True, null=True)
    
    profile_img = CloudinaryField('image', blank=True, null=True)

    class Roles(models.TextChoices):
        ADMIN = 'admin', 'ADMIN'
        STAFF = 'staff', 'STAFF'
        USER = 'user', 'USER'

    role = models.CharField(
        max_length=10,
        choices=Roles.choices,
        default=Roles.USER
    )

    class ActiveStatus(models.TextChoices):
        ACTIVE = 'active', 'ACTIVE'
        INACTIVE = 'inactive', 'INACTIVE'

    status = models.CharField(
        max_length=10,
        choices=ActiveStatus.choices,
        default=ActiveStatus.ACTIVE
    )
    referral_code = models.CharField(max_length=20, unique=True, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'  # Use email to log in
    REQUIRED_FIELDS = ['username']  # Required when using createsuperuser

    def __str__(self):
        return f"{self.username} ({self.email})"

    def is_admin(self):
        return self.role == self.Roles.ADMIN

    def is_staff_user(self):
        return self.role == self.Roles.STAFF

    def is_normal_user(self):
        return self.role == self.Roles.USER
    
    

    class Meta:

        db_table = "users"


class AddressModel(models.Model):
    
    id = models.UUIDField(verbose_name="ID", primary_key=True, default=uuid4)
    full_name = models.CharField(verbose_name="full_name",max_length=100,blank=True,null=True)
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
    user = models.ForeignKey(
        User,  # Reference custom User model
        verbose_name="User",
        on_delete=models.CASCADE,
        related_name='addresses'
    )

    class Meta:
        verbose_name = "Address"

    def __str__(self):
        return f"{self.type} - {self.street_address}, {self.city}"
    
    def addaddress(self,full_name,address_type,alternate_phone_number,street_address,city,state,postal_code,country,user):
        normalized_phone= int(str(alternate_phone_number).replace('+91',''))
        existing = AddressModel.objects.filter(
        user=user,
        full_name=full_name,
        type=address_type,
        alternate_phone_number=normalized_phone,
        street_address=street_address,
        city=city,
        state=state,
        postal_code=postal_code,
        country=country
        )
        if existing.exists():
            return {"status":"error","message":"This address already exists in your address book."}
        
        self.full_name=full_name
        self.type=address_type
        self.alternate_phone_number=normalized_phone
        self.street_address=street_address
        self.city=city
        self.state=state
        self.postal_code=postal_code
        self.country=country
        self.user=user
        if any(field is None for field in [address_type, alternate_phone_number, street_address, city, state, postal_code, country, user]):
            return {"status":"error","message":f"{self.type} fields cannot be empty"}
        self.full_clean()
        self.save()     

        
        return {"status":"success","message":f"Your new address as been added {self.type} - {self.street_address} - {self.city}"}
        


class ReferralRelationship(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid4,editable=False)
    referrer = models.ForeignKey(User,related_name='referrals_made',on_delete=models.CASCADE)
    referred = models.ForeignKey(User,related_name='referred_by',on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True,editable=False)
    
    class Meta:
        unique_together = (('referrer', 'referred'),)
        ordering=['-created_at']
        
    def __str__(self):
        return f"{self.referrer} referred {self.referred}"
    
    
    
    
    