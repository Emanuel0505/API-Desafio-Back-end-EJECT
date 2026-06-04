from django.urls import path, include
from .views import User_register
from rest_framework import routers

router = routers.DefaultRouter()
router.register('register', User_register, basename='Users')

urlpatterns = [
    path('', include(router.urls)),
]
