from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, FileExtensionValidator
from uuid import uuid4
from django.core.exceptions import ValidationError
from django.conf import settings
from colorfield.fields import ColorField
from users.models import User
from django.utils import timezone
import cloudinary
from cloudinary.models import CloudinaryField

def validate_file_size(value):
    max_size = 5 * 1024 * 1024  # 5MB
    if value.size > max_size:
        raise ValidationError('File size must be less than 5MB.')

class Category(models.Model):
    STATUS_CHOICES = (
        (1, 'Active'),
        (0, 'Inactive'),
    )
    id = models.UUIDField(default=uuid4, primary_key=True, editable=False)
    name = models.CharField(max_length=255,unique=True,blank=False,null=False)  # Renamed from type
    slug = models.CharField(max_length=255, unique=True)
    type = models.CharField(max_length=250,blank=False,null=False)
    status = models.IntegerField(choices=STATUS_CHOICES, default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'categories'
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['name']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.name}"

class Brand(models.Model):
    STATUS_CHOICES = (
        (1, 'Active'),
        (0, 'Inactive'),
    )
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=255, unique=True)
    status = models.IntegerField(choices=STATUS_CHOICES, default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'brands'
        verbose_name = 'Brand'
        verbose_name_plural = 'Brands'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.name}"
    
    



class ProductColor(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    color = ColorField(default='#FFFFFF')
    name = models.CharField(max_length=50,unique=True,blank=False,null=False)

    class Meta:
        db_table = 'product_colors'
        verbose_name = 'Product Color'
        verbose_name_plural = 'Product Colors'
        ordering = ['color']
        
    def __str__(self):
        return f"{self.name}"

class Product(models.Model):
    STATUS_CHOICES = (
        (1, 'Active'),
        (0, 'Inactive'),
    )
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    name = models.CharField(max_length=100)
    slug = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True ,max_length=250)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    status = models.IntegerField(choices=STATUS_CHOICES, default=1)
    is_deleted = models.BooleanField(default=False)
    colors = models.ManyToManyField(ProductColor, related_name='products', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    stock_qty = models.IntegerField(validators=[MinValueValidator(0)])

    class Meta:
        db_table = 'products'
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['status']),
            models.Index(fields=['category']),
            models.Index(fields=['brand']),
        ]

    def __str__(self):
        return f"{self.name}"

    
    def get_best_offer(self):
        """
        Returns the highest discount percentage (ProductOffer or CategoryOffer) for this product.
        """
        product_offer = ProductOffers.objects.filter(product=self, is_active=True).first()
        category_offer = CategoryOffer.objects.filter(category=self.category, is_active=True).first()

        product_discount = product_offer.discount_percentage if product_offer else 0
        category_discount = category_offer.discount_percentage if category_offer else 0

        if product_discount > category_discount:
            return product_offer
        elif category_discount > product_discount:
            return category_offer
        else:
            return None
        
        
    def get_effective_price(self):
        offer = self.get_best_offer()
        if offer:
            discount = (self.price * offer.discount_percentage) / 100
            return self.price - discount

        return self.price

class ProductImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image =  CloudinaryField('image', blank=True, null=True)
    alt_text = models.CharField(max_length=100, blank=True, null=True)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'product_images'
        verbose_name = 'Product Image'
        verbose_name_plural = 'Product Images'
        
    def save(self, *args, **kwargs):
        if self.image and not str(self.image).startswith("http"):
            # Upload to Cloudinary with cropping
            upload_result = cloudinary.uploader.upload(
                self.image,
                folder="product_images",
                transformation={
                    "width": 500,
                    "height": 500,
                    "crop": "fill"
                }
            )
            # Store only the Cloudinary URL
            self.image = upload_result['secure_url']

        super().save(*args, **kwargs)
        

    def __str__(self):
        return f"Image for {self.product.name}"

class ProductReview(models.Model):
    STATUS_CHOICES = (
        (1, 'Active'),
        (0, 'Inactive'),
    )
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='product_reviews')    
    rating = models.DecimalField(max_digits=2, decimal_places=1, validators=[MinValueValidator(0), MaxValueValidator(5)])
    
    review = models.TextField(max_length=5000)
    status = models.IntegerField(choices=STATUS_CHOICES, default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'product_reviews'
        verbose_name = 'Product Review'
        verbose_name_plural = 'Product Reviews'
        indexes = [
            models.Index(fields=['product']),
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return f"Review for {self.product.name} by {self.user}"
    
    



class Comment(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        db_table = 'product_comments'

    def __str__(self):
        return f'Comment by {self.user.email} on {self.product.name}'
    
    
    
class ProductOffers(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_offers')
    discount_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.product.name} - {self.discount_percentage}% Off"

class CategoryOffer(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='category_offers')
    discount_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.category.name} - {self.discount_percentage}% Off"