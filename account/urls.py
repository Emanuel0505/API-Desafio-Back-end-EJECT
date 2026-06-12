from django.urls import path, include
from .views import User_register, User_update, Address_Viewsets, Forgot_Password, Reset_Password
from rest_framework_nested import routers


router = routers.DefaultRouter()
router.register('register', User_register, basename='Users')

router_user = routers.DefaultRouter()
router_user.register('address', Address_Viewsets, basename='Address')

urlpatterns = [
    path('', include(router.urls)),
    path('user/', include(router_user.urls)),

    path('forgot-password/', Forgot_Password.as_view(), name = 'password-reset'),
    path('forgot-password/<str:encoded_pk>/<str:token>', Reset_Password.as_view(),name = 'password-reset'),
    
    path('user/update', User_update.as_view() ,name = 'user-update'),
]
