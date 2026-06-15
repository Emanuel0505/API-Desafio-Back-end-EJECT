from rest_framework import serializers
import re
from validate_docbr import CPF
from datetime import date, datetime

def cpf_invalid(cpf_number):
    cpf = CPF()
    cpf_valid = cpf.validate(cpf_number)
    return not cpf_valid

def phone_invalid(phone):
    model = '[0-9]{2} [0-9] [0-9]{4}-[0-9]{4}'
    response = re.findall(model,phone)
    return not response

def name_invalid(name):
    model = r"^[A-za-zÀ-ü'.\s]+$"
    response = re.findall(model, name)
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
    Custom password validation
    """

    if len(value) < 8:
        raise serializers.ValidationError('Password: Must contain a minimum of 8 characters.')
    
    if not re.search(r'[^a-zA-Z0-9]', value):
        raise serializers.ValidationError('Password: Must contain at least 1 special character.')
    
    if not re.search(r'[A-Z]', value):
        raise serializers.ValidationError('Password: Must contain at least 1 uppercase letter.')
    
    if not re.search(r'[a-z]', value):
        raise serializers.ValidationError('Password: Must contain at least 1 lowercase letter.')
    
    if not re.search(r'[0-9]', value):
        raise serializers.ValidationError('Password: Must contain at least 1 number.')
    
    return value

def number_card_invalid(num):
    model = '[0-9]{4} [0-9]{4} [0-9]{4} [0-9]{4}'
    response = re.findall(model, num)
    return not response

def date_invalid(date):
    model = r"^(0[1-9]|1[0-2])[/][0-9]{2}$"
    response = re.findall(model, date)
    return not response

def expired_date_invalid(date):
    month, year  = re.split(r'/', date)

    month = int(month)
    year = int(f'20{year}')

    date_exp = datetime(year,month,1)

    # expired date
    if datetime.now() >= date_exp:
        return True
    
    # date not expired
    return False
        