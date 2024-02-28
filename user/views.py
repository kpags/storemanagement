from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import User
from .serializers import UserSerializer
from .validate import *
from .functions import UserFunctions
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
import jwt, datetime

@api_view(['GET'])
def getUsers(request):
    token = request.COOKIES.get('jwt')
    
    if not token:
        return Response({"message": "No users logged in"})
    
    try:
        payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        currentUser = User.objects.filter(id=payload['id']).first()

        UserValidate.validateUserAccess(currentUser.level)

        user = User.objects.all()
        serializer = UserSerializer(user, many=True)

        return Response(serializer.data)
    except ValidationError as ve:
        return Response(f'error: {ve.messages}')
    except jwt.ExpiredSignatureError:
        return Response({"error": "No Superuser/Administrator logged in"})

@api_view(['POST'])
def addUser(request):
    token = request.COOKIES.get('jwt')

    if not token:
        return Response({"message": "No users logged in"})
    
    try:
        payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        currentUser = User.objects.filter(id=payload['id']).first()

        UserValidate.validateUserAccess(currentUser.level)

        serializer = UserFunctions.addUser(request)

        return Response(serializer.data)
    except ValidationError as ve:
        return Response(f'Error: {ve.messages}')
    except jwt.ExpiredSignatureError:
        return Response({"error": "No Superuser/Administrator logged in"})

@api_view(['PUT'])
def updateUser(request, id):
    token = request.COOKIES.get('jwt')

    if not token:
        return Response({"message": "No users logged in"})

    try:
        payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        currentUser = User.objects.filter(id=payload['id']).first()

        UserValidate.validateUserAccess(currentUser.level)

        user = User.objects.filter(id=id).first()
        if not user:
            return Response({"error": "User not found"}, status=404)

        return UserFunctions.updateUser(user, id, request)
    except ValidationError as ve:
        return Response(f'error: {ve.messages}')
    except jwt.ExpiredSignatureError:
        return Response({"error": "No Superuser/Administrator logged in"})

@api_view(['DELETE'])
def deleteUser(request, id):
    token = request.COOKIES.get('jwt')

    if not token:
        return Response({"message": "No users logged in"})

    try:
        payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        currentUser = User.objects.filter(id=payload['id']).first()

        UserValidate.validateUserAccess(currentUser.level)

        user = User.objects.get(id=id)  
        if not user:
            return Response({"error": "User not found"}, status=404)
        else:
            user.delete()
            return Response({"message": "User " + user.username + " deleted successfully"})
    except ValidationError as ve:
        return Response(f'error: {ve.messages}')
    except jwt.ExpiredSignatureError:
        return Response({"error": "No Superuser/Administrator logged in"})

@api_view(['POST'])
def login(request):
    username = request.data.get('username', None)

    user = User.objects.filter(username=username).first()

    if user is not None:
        return UserFunctions.loginUser(user, request)
    else:
        return Response({"message": "User not found"})
    
@api_view(['POST'])
def logout(request):
    token = request.COOKIES.get('jwt')

    if not token:
        return Response({"message": "No user logged in"})

    response = Response()
    response.delete_cookie('jwt')
    response.data = {
        'message': 'User logged out'
    }

    return response

@api_view(['GET'])
def getJWT(request):
    token = request.COOKIES.get('jwt')

    if not token:
        return Response({"message": "No users logged in"})

    try:
        payload = jwt.decode(token, 'secret', algorithms=['HS256'])

        user = User.objects.filter(id=payload['id']).first()
        serializer = UserSerializer(user)

        return Response(serializer.data)
    except jwt.ExpiredSignatureError:
        return Response({"error": "Not Authenticated or No user logged in"})
    except jwt.exceptions.DecodeError:
        return Response({"error": "Decoded Error"})

    
    