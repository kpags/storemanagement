from .validate import UserValidate
from .serializers import UserSerializer
import jwt, datetime
from rest_framework.response import Response


class UserFunctions():
    def addUser(request):
        UserValidate.validateUsername(request.data.get('username', None), 'POST', None)
        UserValidate.validatePassword(request.data.get('password', None))
        UserValidate.validateEmail(request.data.get('email', None), 'POST', None)
        UserValidate.validateLevel(request.data.get('level', None))

        serializer = UserSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

        return serializer
    
    def updateUser(user, id, request):
        UserValidate.validateUsername(request.data.get('username', None), 'PUT', id)
        UserValidate.validatePassword(request.data.get('password', None))
        UserValidate.validateEmail(request.data.get('email', None), 'PUT', id)
        UserValidate.validateLevel(request.data.get('level', None))

        serializer = UserSerializer(user, data=request.data, partial=True)    
        
        if serializer.is_valid():
            serializer.save()
            return Response({"message" : "User " + user.username + " updated successfully"})
        else:
            return Response(serializer.errors, status=400)
        
    def loginUser(user, request):
        payload = {
            'id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=60),
            'iat': datetime.datetime.utcnow()
        }

        token = jwt.encode(payload, 'secret', algorithm='HS256')
    
        response = Response()
        response.set_cookie(key='jwt', value=token.decode('utf-8'), httponly=True)
        response.data = {
            "message": user.username + " logged in",
            'jwt': token
        }
        
        return response