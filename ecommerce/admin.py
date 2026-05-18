from django.contrib import admin
from .models import User, Category, Product, Review, Address

@admin.register(User)
class Useradmin(admin.ModelAdmin):
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal info", {"fields": ("fullname", "email", "cpf", "phone", "date_of_birth")}),
        ("Permissions", {"fields": ("is_active" , "usertype", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

@admin.register(Category)
class Categoryadmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Product)
class Productadmin(admin.ModelAdmin):
    list_display = ('title', 'content', 'color', 'color', 'size', 'amount', 'category',)

@admin.register(Review)
class Reviewadmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'content', 'star', 'date_created', )

@admin.register(Address)
class Address(admin.ModelAdmin):
    list_display = ('cep', 'state', 'city', 'neightborhood', 'street', 'number', )