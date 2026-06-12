from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.text import slugify
from colorfield.fields import ColorField
from account.models import User
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
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products')
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

    #retorna products/id_nameproduct/number.jpg
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
        return f'Product {self.product.title} and color {self.color_name}'
    
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


