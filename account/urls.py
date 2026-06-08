from django.urls import path, include
from .views import User_register, User_update, Forgot_Password, Reset_Password
from rest_framework import routers


router = routers.DefaultRouter()
router.register('register', User_register, basename='Users')

urlpatterns = [
    path('', include(router.urls)),
    path('forgot-password/', Forgot_Password.as_view(), name = 'password-reset'),
    path('forgot-password/<str:encoded_pk>/<str:token>', Reset_Password.as_view(),name = 'password-reset'),
    path('user/update', User_update.as_view() ,name = 'user-update'),
]
