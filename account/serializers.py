from rest_framework import serializers
from .models import User
from .validators import *
from datetime import date

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
            'date_of_birth',
            'usertype'
        ]
        extra_kwargs = {
            'password': {'write_only' : True}

        }

    def validate_password(self, value):
        """
        Validação customizada para senha
        """

        if len(value) < 8:
            raise serializers.ValidationError('Senha: Deve conter no minimo 8 caracteres.')
        
        if not re.search(r'[^a-zA-Z0-9]', value):
            raise serializers.ValidationError('Senha: Deve conter no minimo 1 caractere especial.')
        
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError('Senha: Deve conter no minimo 1 letra maiúscula.')
        
        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError('Senha: Deve conter no minimo 1 letra minúscula.')
        
        if not re.search(r'[0-9]', value):
            raise serializers.ValidationError('Senha: Deve conter no minimo 1 número.')
        
        return value

    def validate_date_of_birth(self, value):
        if value == None:
            raise serializers.ValidationError('Data de Nascimento: O campo não pode estar em branco.')

        if value > date.today():
            raise serializers.ValidationError('Data de Nascimento: Não pode ser uma data futura.')
        
        if date_of_birth_invalid_age(value):
            raise serializers.ValidationError('Data de Nascimento: Ter no mínimo 18 anos.')
        

        
        return value

    def validate_fullname(self, value):
        
        if not value.isalpha():
            raise serializers.ValidationError('Nome: Não deve conter números e caracteres especiais.')
        
        if len(value) < 3:
            raise serializers.ValidationError('Name: Ter no mínimo 3 letras.')
        
        return value

    def validate(self, attrs):

        if cpf_invalid(attrs['cpf']):
            raise serializers.ValidationError('CPF: Deve conter um valor válido')
        
        if phone_invalid(attrs['phone']):
            raise serializers.ValidationError('Celular: Seguir o modelo (84) 9 9999-9999')
        
        return attrs

    def create(self, validated_data):
        """
        Criação do Usuario 
        """

        validated_data.pop('passeord_confirm', None)

        user = User.objects.create_user(**validated_data)

        return user
            


