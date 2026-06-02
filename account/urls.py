from django.urls import path, include
from .views import User_Viewsets
from rest_framework import routers

router = routers.DefaultRouter()
router.register('users', User_Viewsets, basename='Users')

urlpatterns = [
    path('', include(router.urls)),

]
