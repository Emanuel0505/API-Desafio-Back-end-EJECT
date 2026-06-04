from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from .models import User
from .serializers import User_Serializer

class User_register(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    authentication_classes = [TokenAuthentication]
    queryset = User.objects.all()
    serializer_class =  User_Serializer
    http_method_names = ['post']