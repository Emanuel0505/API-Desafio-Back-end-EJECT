import re
from validate_docbr import CPF
from datetime import date

def cpf_invalid(cpf_number):
    cpf = CPF()
    cpf_valid = cpf.validate(cpf_number)
    return not cpf_valid

def name_invalid(name):
    return not name.isalpha()

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