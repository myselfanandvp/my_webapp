from django.db import models
from uuid import uuid4
from users.models import User
from products.models import Product,ProductColor
# Create your models here.
class WishList(models.Model):
    id = models.UUIDField(verbose_name="ID",primary_key=True,default=uuid4)
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name="wishlists")
    product = models.ForeignKey(Product,on_delete=models.CASCADE,related_name="wishlisted_by")
    color= models.ForeignKey(ProductColor,on_delete=models.SET_NULL, null=True, blank=True, related_name='wishlist_color')
    added_at= models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = 'wishlists'
        unique_together = ('user', 'product','color')
        
    def __str__(self):
        return f"{self.user} added {self.product} to wishlist"