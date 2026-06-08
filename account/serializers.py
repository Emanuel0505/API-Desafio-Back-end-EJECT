from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_decode

from rest_framework import serializers
from .models import User
from .validators import *
from datetime import date

class User_Serializer(serializers.ModelSerializer):
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'id', 
            'fullname',
            'cpf',
            'email',
            'password',
            'password_confirm',
            'phone',
            'date_of_birth',
            'usertype'
        ]
        extra_kwargs = {
            'password': {'write_only' : True}

        }

    def validate_password(self, value):
        return validate_password_unique(value)

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
        
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError('password_confirm: Senhas não coincidem')

        return attrs

    def create(self, validated_data):
        """
        Criação do Usuario 
        """

        validated_data.pop('password_confirm', None)

        user = User.objects.create_user(**validated_data)

        return user
    
    def update(self, instance, validated_data):
        validated_data.pop('password_confirm', None)
        
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance

class User_update_Serializer(serializers.ModelSerializer):
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'fullname',
            'cpf',
            'email',
            'password',
            'password_confirm',
            'phone',
            'date_of_birth',
        ]
        extra_kwargs = {
            'password': {'write_only' : True}

        }
    def update(self, instance, validated_data):
        validated_data.pop('password_confirm', None)
        
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance


class Email_Serializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    class Meta:
        fields = ('email',)

class Reset_Password_Serializer(serializers.Serializer):
    password = serializers.CharField(write_only = True)
    confirm_password = serializers.CharField(write_only = True)

    class Meta:
        fields = ('password','confirm_password',)

    def validate_password(self, value):
        return validate_password_unique(value)
    
    def validate(self, attrs):
        if not attrs['password'] == attrs['confirm_password']:
            raise serializers.ValidationError('As senhas não coicidem')
        else:
            password = attrs.get('password')
            token = self.context.get('kwargs').get('token')
            encoded_pk = self.context.get('kwargs').get('encoded_pk')
            
            if token is None or encoded_pk is None:
                serializers.ValidationError('Missing data')

            pk = urlsafe_base64_decode(encoded_pk).decode()
            user = User.objects.get(pk=pk)

            if not PasswordResetTokenGenerator().check_token(user, token):
                raise serializers.ValidationError('O token é invalido')
            
            user.set_password(password)
            user.save()
        return attrs
    