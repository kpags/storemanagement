from .models import User
from django.core.exceptions import ValidationError
import re

class UserValidate():
    def validateUsername(username, method, id):
        if len(username) > 20 or len(username) < 5:
            raise ValidationError('Username must have 5 to 20 characters')
        
        if User.objects.filter(username=username).exists() and method == 'POST':
            raise ValidationError('Username already exists')
        
        if id:
            if User.objects.filter(username=username).exclude(id=id):
                raise ValidationError('Cannot update username that already exists')
        
    def validatePassword(password):
        if len(password) < 5:
            raise ValidationError('Password must be greater than 4 characters')
        
    def validateEmail(email, method, id):
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'

        if not re.fullmatch(regex, email):
            raise ValidationError('Email format not valid')
        
        if User.objects.filter(email=email).exists() and method == 'POST':
            raise ValidationError('Email already exists')
        
        if id:
            if User.objects.filter(email=email).exclude(id=id):
                raise ValidationError('Cannot update email that already exists')
        
    def validateLevel(level):
        validLevels = ['USER','ADMINISTRATOR', 'SUPERUSER']

        if not level.upper() in validLevels:
            raise ValidationError('Level not valid. Select between USER, ADMINISTRATOR, SUPERUSER')
        
    def validateUserAccess(level):
        if level == 'USER':
            raise ValidationError("You don't have the permission to access this feature")