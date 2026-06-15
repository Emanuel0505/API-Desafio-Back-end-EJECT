from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.text import slugify
from colorfield.fields import ColorField
from account.models import User, card
import os

class Category(models.Model):
    name = models.CharField()

    def __str__(self):
        return self.name

class Product(models.Model):
    title = models.CharField(max_length=150, unique=True)
    content = models.TextField()
    price = models.DecimalField(max_digits=9,decimal_places=2, blank= False, null=False, default=100)
    category = models.ForeignKey(Category, blank=False, null= False, on_delete=models.PROTECT)
    active = models.BooleanField(default=True)
    shopkeeper = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products')
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title

def path_product_image(instance, filename):
    ext = filename.split('.')[-1]
    if instance.product and instance.product.id:
        count_image = instance.product.images.count()
    else:
        count_image = 0
        
    image_name = f'{count_image+1}.{ext}'

    product_name = slugify(instance.product.title)
    product_path = f'{instance.product.id}_{product_name}'

    # returns products/id_product_name/number.jpg
    return os.path.join('ecommerce/products', product_path, image_name)

class Images_product(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=path_product_image)

class Stock(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock')
    amount = models.PositiveIntegerField(null=False, blank=False, default=1)
    color_name = models.CharField(max_length=50, null=False, blank=False, default='Black')
    color_hexadecimal = ColorField(default = '#000000',  null = False, blank = False)
    size = models.CharField(null= False, blank= False)

    def __str__(self):
        return f'Product {self.product.title}, color {self.color_name} and size {self.size}'
    
    def save(self, *args, **kwargs):
        self.color_name = self.color_name.lower()
        self.size = self.size.upper()

        return super().save(*args, **kwargs)

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='review') 
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='review')
    content = models.TextField(blank=True, null=True)
    star = models.PositiveSmallIntegerField(blank=False, null=False)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.content

class contact_support_email(models.Model):
    email = models.EmailField(blank=False, null=False)
    name = models.CharField(max_length=255, blank=False, null=False)
    subject = models.CharField(max_length=255, blank=False, null=False)
    content = models.TextField(blank=False, null=False)

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart', blank=False, null=False)
    date_update = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'Cart of {self.user}'
    
class cart_item(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='item')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variations = models.ForeignKey(Stock, on_delete=models.CASCADE, null=False, blank=False)
    amount = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'Item: {self.product.title}'
    
class orders(models.Model):
    STATUS_ORDERS = {
        ('CREATED', 'CREATED / Awaiting Payment'),
        ('PAID', 'Paid'),
        ('SEPARATION', 'Separating'),
        ('SENT', 'Sent'),
        ('DELIVERED', 'Delivered'),
        ('CANCELED', 'Canceled'),
    }

    user = models.ForeignKey(User, on_delete=models.PROTECT, blank=False, related_name= 'orders')
    status = models.CharField(choices=STATUS_ORDERS, default='CREATED')
    total_price = models.IntegerField(blank=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

class Order_item(models.Model):
    order = models.ForeignKey(orders, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    variations = models.ForeignKey(Stock, on_delete=models.PROTECT)
    amount = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=9, decimal_places=2)

    def __str__(self):
        return f'{self.amount} x {self.product.price}'
    
class Payment(models.Model):
    PAYMENT_TYPES = [
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('pix', 'PIX'),
        ('boleto', 'Boleto'),
    ]

    order = models.ForeignKey(orders, on_delete=models.CASCADE, related_name='payments')
    Card = models.ForeignKey(card, on_delete=models.PROTECT, related_name='card', blank=True, null=True)
    type = models.CharField(max_length=20, choices=PAYMENT_TYPES)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.order} the payment method {self.type}'
    