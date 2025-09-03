from django.db import models
from products.models import Product,ProductColor
from users.models import User
from uuid import uuid4

# Create your models here.


class Cart(models.Model):
 
    
    id = models.UUIDField(verbose_name="ID", primary_key=True,
                          editable=False, default=uuid4)
    product = models.ForeignKey(
        Product,related_name='cart_items',on_delete=models.CASCADE)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='user_items')
    color=models.ForeignKey(ProductColor,on_delete=models.SET_NULL,related_name="product_cart_color",blank=True,null=True)
    quantity = models.PositiveIntegerField(default=0)
    
 

    class Meta:
        db_table = "cart"
        unique_together = ('user', 'product','color')

    def __str__(self):
        return f"Cart({self.user.email} - {self.product.name})"

    @property
    def total_price(self):
        return self.product.price * self.quantity
    @property
    def product_price(self):
        return self.product.price

    def increment_quantity(self):
        if self.quantity<5:
            self.quantity+=1
            self.product.stock_qty -= 1
            self.product.save()
            self.save()
        return self.quantity
        
        

    def decrement_quantity(self):
        if self.quantity>1:
            self.quantity-=1
            self.product.stock_qty+=1
            self.product.save()
            self.save()
        return self.quantity
    
    def remove_product(self):
        self.product.stock_qty+= self.quantity
        self.product.save()
        return self.delete()
        
        
    
  