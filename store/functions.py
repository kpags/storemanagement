from .validate import StoreValidate
from .serializers import StoreSerializer
import jwt, datetime
from rest_framework.response import Response
from user.models import User
from .models import Store

class StoreFunctions():
    def addStore(user, request):
        StoreValidate.validateName(request.data.get('name', None), 'POST', None)
            
        name = request.data.get('name', None)
        type = request.data.get('type', None)
        address = request.data.get('address', None)

        store = Store.objects.create(name=name, type=type, address=address, owner=user)
        store.save()

        return store
    
    def updateStore(user, store, request, id):
        StoreValidate.validateName(request.data.get('name', None), 'PUT', id)

        serializer = StoreSerializer(store, data=request.data)   

        if serializer.is_valid():
            serializer.save()
        
        return serializer