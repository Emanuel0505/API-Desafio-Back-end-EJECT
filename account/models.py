from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone

#classe para criação de usario e super usuario via terminal
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("O email é obrigatório")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser precisa ter is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser precisa ter is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    USERTYPE = {
        ('C','Cliente'),
        ('L','Lojista')
    }
    fullname = models.CharField(max_length=255)
    date_of_birth = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=16)
    cpf = models.CharField(max_length=11)
    email = models.EmailField(null=False, unique=True)
    usertype = models.CharField(choices=USERTYPE, default='C')
    created_at = models.DateField(default=timezone.now)

    username = None
    last_login = None
    last_name = None
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.fullname
    
class Address(models.Model):
    name = models.CharField(blank=False, null=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='address')
    cep = models.CharField(max_length=8, blank=False, null=False)
    state = models.CharField(max_length=2)
    city = models.CharField()
    neightborhood = models.CharField()
    street = models.CharField()
    number = models.CharField()
    
    def __str__(self):
        return self.cep