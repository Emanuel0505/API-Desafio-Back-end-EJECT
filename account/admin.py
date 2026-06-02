from django.contrib import admin
from .models import User

@admin.register(User)
class Useradmin(admin.ModelAdmin):
    fieldsets = (
        (None, {"fields": ("fullname", "cpf", "phone", "date_of_birth", "email", "password", "usertype")}),
    )

