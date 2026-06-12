from django.contrib import admin
from .models import User, Address

@admin.register(User)
class Useradmin(admin.ModelAdmin):
    fieldsets = (
        (None, {"fields": ("fullname", "cpf", "phone", "date_of_birth", "email", "password", "usertype")}),
    )

@admin.register(Address)
class Addressadmin(admin.ModelAdmin):
    list_display = ('cep', 'state', 'city', 'neightborhood', 'street', 'number', )