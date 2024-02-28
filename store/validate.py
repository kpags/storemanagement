from .models import Store
from django.core.exceptions import ValidationError
import re

class StoreValidate():
    def validateName(name, method, id):
        if Store.objects.filter(name=name).exists() and method == 'POST':
            raise ValidationError('Store already exists')
        
        if id:
            if Store.objects.filter(name=name).exclude(id=id):
                raise ValidationError('Cannot update store name that already exists')
            
    def validateUserAccess(level):
        if level == 'USER':
            raise ValidationError("You don't have the permission to access this feature")