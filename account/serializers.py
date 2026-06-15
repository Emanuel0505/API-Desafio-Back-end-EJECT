from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_decode

from rest_framework import serializers

from datetime import date
import re
import requests

from .models import User, Address, card
from .validators import *

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
            raise serializers.ValidationError('Date of birth: The field cannot be blank.')

        if value > date.today():
            raise serializers.ValidationError('Date of birth: Cannot be a future date.')
        
        if date_of_birth_invalid_age(value):
            raise serializers.ValidationError('Date of birth: Must be at least 18 years old.')
        
        return value

    def validate_fullname(self, value):
        
        if name_invalid(value):
            raise serializers.ValidationError('Name: Should not contain numbers and special characters.')
        
        if len(value) < 3:
            raise serializers.ValidationError('Name: Must have at least 3 letters.')
        
        return value

    def validate(self, attrs):

        if cpf_invalid(attrs['cpf']):
            raise serializers.ValidationError('CPF: Must contain a valid value')
        
        if phone_invalid(attrs['phone']):
            raise serializers.ValidationError('Phone: Follow the pattern (84) 9 9999-9999')
        
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError('password_confirm: Passwords do not match')
            

        return attrs

    def create(self, validated_data):
        """
        User creation
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

class Address_Serializer(serializers.ModelSerializer):

    user = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = Address
        fields = [
            'user',
            'name',
            'cep',
            'state',
            'city',
            'neightborhood',
            'street',
            'number',
        ]

    def validate_cep(self, value):
        
        url = f'https://brasilapi.com.br/api/cep/v1/{value}'
        response = requests.get(url)

        if response.status_code == 400:
            raise serializers.ValidationError('CEP must contain 8 digits')

        if response.status_code == 404:    
            raise serializers.ValidationError('CEP not found')
        
        if response.status_code == 500:
            raise serializers.ValidationError('CEP: Error when querying the CEP')

        return value
    
    def validate_name(self, value):
        if not value.isalpha():
            raise serializers.ValidationError('Name: Should not contain numbers and special characters')

        if not len(value) <=50:
            raise serializers.ValidationError('Name: Maximum of 50 characters')
        
        return value
        
    def validate_state(self, value):
        if not len(value) == 2:
            raise serializers.ValidationError('State: Provide the abbreviation')
        
        if not value.isalpha():
            raise serializers.ValidationError('State: Should not contain numbers and special characters')

        return value
    
    def validate_number(self, value):
        if not value.isdigit():
            raise serializers.ValidationError('Number: Should not contain letters and special characters')

        return value

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
            raise serializers.ValidationError('Passwords do not match')
        else:
            password = attrs.get('password')
            token = self.context.get('kwargs').get('token')
            encoded_pk = self.context.get('kwargs').get('encoded_pk')
            
            if token is None or encoded_pk is None:
                serializers.ValidationError('Missing data')

            pk = urlsafe_base64_decode(encoded_pk).decode()
            user = User.objects.get(pk=pk)

            if not PasswordResetTokenGenerator().check_token(user, token):
                raise serializers.ValidationError('The token is invalid')
            
            user.set_password(password)
            user.save()
        return attrs

class Card_Serializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = card
        fields = [
            'id',
            'user',
            'surname',
            'number',
            'name',
            'cvv',
            'validity_date',
        ]

    def validate_surname(self, value):
        if not value.isalpha():
            raise serializers.ValidationError('Surname: without special characters and numbers.')

        return value
    
    def validate_number(self,value):
        if number_card_invalid(value):
            raise serializers.ValidationError('Number: Follow the pattern 0000 0000 0000 0000')

        return value
    
    def validate_name(self, value):
        if name_invalid(value):
            raise serializers.ValidationError('Name: Should not contain special characters and numbers.')
        
        if not len(value)<=26:
            raise serializers.ValidationError('Name: Must contain up to 26 characters.')

        return value
    
    def validate_cvv(self, value):
        if not value.isdigit():
            raise serializers.ValidationError('CVV: Should contain only numbers.')

        if not len(value) == 3:
            raise serializers.ValidationError('CVV: Should contain 3 digits.')

        return value

    def validate_validity_date(self, value):
        if date_invalid(value):
            raise serializers.ValidationError('Date: Follow the pattern 00/00')
        
        if expired_date_invalid(value):
            raise serializers.ValidationError('Date: Card expiration date has passed')
        
        return value

    


    


        