from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.db.models.functions import Now

class User(AbstractBaseUser):
    fullname = models.CharField(max_length=255)
    date_of_birth = models.DateField()
    phone = models.CharField(max_length=13)
    cpf = models.CharField(max_length=11)
    #created = (não sei já tem no do proprio django)

    def __str__(self):
        return self.fullname

class Category(models.Model):
    name = models.CharField

    def __str__(self):
        return self.name

class Product(models.Model):
    TAMANHO = (
        ('P', 'Pequeno'),
        ('M', 'Médio'),
        ('G', 'Grande'),
        ('GG', 'Extra-Grande'),
    )

    title = models.CharField(max_length=255)
    content = models.TextField()
    color = models.CharField()
    size = models.CharField(max_length=2, choices= TAMANHO)
    amount = models.PositiveIntegerField()
    category = models.ForeignKey(Category, blank=False, null= False, on_delete=models.PROTECT)

    def __str__(self):
        return self.title

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='review') 
    content = models.TextField()
    star = models.PositiveSmallIntegerField(default=0, blank=False, null=False)
    date_created = models.DateTimeField(db_default=Now())
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='review')

    def __str__(self):
        return self.content

class Address(models.Model):
    cep = models.CharField(max_length=8, blank=False, null=False)
    state = models.CharField(max_length=2)
    city = models.CharField()
    neightborhood = models.CharField()
    street = models.CharField()
    number = models.CharField()
    
    def __str__(self):
        return self.cep


