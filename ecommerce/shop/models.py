from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/')

    def __str__(self):
        return self.name

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='cart_items')
    quantity = models.PositiveIntegerField(default=1)
    payment_method = models.CharField(max_length=20, choices=[('COD', 'Cash on Delivery'), ('Online', 'Online Payment')], null=True, blank=True)
    def __str__(self):
        return f"{self.user.username} - {self.product.name} (x{self.quantity})"

    @property
    def total_price(self):
        return self.quantity * self.product.price