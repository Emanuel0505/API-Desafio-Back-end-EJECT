from django.urls import path, include
from .views import User_register, Password_Reset, Reset_Password
from rest_framework import routers


router = routers.DefaultRouter()
router.register('register', User_register, basename='Users')

urlpatterns = [
    path('', include(router.urls)),
    path('forgot-password/', Password_Reset.as_view(), name = 'password-reset'),
    path('forgot-password/<str:encoded_pk>/<str:token>', Reset_Password.as_view() ,name = 'password-reset'),
]
