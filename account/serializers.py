from rest_framework import serializers
from .models import User

class User_Serializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 
            'fullname',
            'cpf',
            'email',
            'password',
            'phone',
            'usertype'
        ]
        extra_kwargs = {
            'password': {'write_only' : True}

        }