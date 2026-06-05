from rest_framework import serializers
import re
from validate_docbr import CPF
from datetime import date

def cpf_invalid(cpf_number):
    cpf = CPF()
    cpf_valid = cpf.validate(cpf_number)
    return not cpf_valid

def phone_invalid(phone):
    model = '[0-9]{2} [0-9] [0-9]{4}-[0-9]{4}'
    response = re.findall(model,phone)
    return not response

def date_of_birth_invalid_age(value):
    minimum_age = 18
    year = date.today().year
    month = date.today().month
    day = date.today().day
    
    if (year - value.year) < minimum_age:
        return True
    elif value.month > month:
        return True
    elif value.day > day:
        return True
    
def validate_password_unique(value):
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