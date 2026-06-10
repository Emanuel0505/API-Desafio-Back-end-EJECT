from django.contrib import admin
from .models import *

@admin.register(Category)
class Categoryadmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Product)
class Productadmin(admin.ModelAdmin):
    list_display = ('title', 'content','category',)

@admin.register(Images_product)
class Images_productadmin(admin.ModelAdmin):
    list_display = ('image', 'product')
@admin.register(Stock)
class Stockadmin(admin.ModelAdmin):
    list_display = ('product', 'amount', 'color_name', 'color_hexadecimal', 'size')

@admin.register(Review)
class Reviewadmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'content', 'star', 'date_created', )

@admin.register(Address)
class Addressadmin(admin.ModelAdmin):
    list_display = ('cep', 'state', 'city', 'neightborhood', 'street', 'number', )
    