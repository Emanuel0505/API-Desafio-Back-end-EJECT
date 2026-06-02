from rest_framework import viewsets
from .models import User
from .serializers import User_Serializer


class User_Viewsets(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class =  User_Serializer

