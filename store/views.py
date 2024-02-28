from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Store
from .serializers import StoreSerializer
from django.core.exceptions import *
from .validate import StoreValidate
from .functions import StoreFunctions
from user.models import User
import jwt, datetime, time

@api_view(['GET'])
def getStores(request):
    token = request.COOKIES.get('jwt')

    if not token:
        return Response({"message": "No users logged in"})

    try:
        payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        user = User.objects.filter(id=payload['id']).first()
        
        StoreValidate.validateUserAccess(user.level)

        store = Store.objects.all()
        serializer = StoreSerializer(store, many=True)

        return Response(serializer.data)
    except ValidationError as ve:
        return Response(f'error: {ve.messages}')
    except jwt.ExpiredSignatureError:
        return Response({"error": "User not authenticated! Login again"})
    
@api_view(['GET'])
def getUserStores(request):
    token = request.COOKIES.get('jwt')

    if not token:
        return Response({"message": "No users logged in"})
        
    try:
        payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        user = User.objects.filter(id=payload['id']).first()

        store = Store.objects.filter(owner=user.id)
        serializer = StoreSerializer(store, many=True)

        return Response(serializer.data)
    except ValidationError as ve:
        return Response(f'error: {ve.messages}')
    except jwt.ExpiredSignatureError:
        return Response({"error": "User not authenticated! Login again"})

@api_view(['GET'])
def getStoreDetails(request, id):
    token = request.COOKIES.get('jwt')

    if not token:
        return Response({"message": "No users logged in"})

    try:
        payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        user = User.objects.filter(id=payload['id']).first()

        store = Store.objects.filter(id=id).first()

        if not store:
            raise ValidationError("Store does not exists")
        
        if user.level == 'USER':
            if store.owner != user:
                raise ValidationError("You don't have the permission to view other stores")
        
        serializer = StoreSerializer(store)

        return Response(serializer.data)
    except ValidationError as ve:
        return Response(f'error: {ve.messages}')
    except jwt.ExpiredSignatureError:
        return Response({"error": "User not authenticated! Login again"})

@api_view(['POST'])
def addStore(request):
    token = request.COOKIES.get('jwt')

    if not token:
        return Response({"message": "No users logged in"})
    
    try:
        payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        user = User.objects.filter(id=payload['id']).first()

        store = StoreFunctions.addStore(user, request)
        return Response({'message':'Store ' + store.name + " owned by " + user.username + " created"})
    except ValidationError as ve:
        return Response(f'error: {ve.messages}')
    except jwt.ExpiredSignatureError:
        return Response({"error": "User not authenticated! Login again"})

@api_view(['PUT'])
def updateStore(request, id):
    token = request.COOKIES.get('jwt')
    
    if not token:
        return Response({"message": "No users logged in"})
    
    try:
        payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        user = User.objects.filter(id=payload['id']).first()

        store = Store.objects.filter(id=id).first()

        if not store:
            raise ValidationError({"error": "Store not found"})
        
        if user.level == "USER":
            if store.owner != user:
                raise ValidationError("You don't have the permission to edit other stores")
    
        serializer = StoreFunctions.updateStore(user, store, request, id)

        return Response(serializer.data)
    except ValidationError as ve:
        return Response(f'error: {ve.messages}')
    except jwt.ExpiredSignatureError:
        return Response({"error": "User not authenticated! Login again"})
    
@api_view(['DELETE'])
def deleteStore(request, id):
    token = request.COOKIES.get('jwt')
    
    if not token:
        return Response({"message": "No users logged in"})
    
    try:    
        payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        user = User.objects.filter(id=payload['id']).first()

        store = Store.objects.filter(id=id).first()

        if not store:
            raise ValidationError({"error": "Store not found"})
        
        if user.level == "USER":
            if store.owner != user:
                raise ValidationError("You don't have the permission to delete other stores")
            
        store.delete()
        return Response({"message": "Store " + store.name + " deleted successfully"})
    except ValidationError as ve:
        return Response(f'error: {ve.messages}')
    except jwt.ExpiredSignatureError:
        return Response({"error": "User not authenticated! Login again"})