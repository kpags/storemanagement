from django.test import TestCase
from django.urls import reverse
from rest_framework_jwt.settings import api_settings
from rest_framework import status
from .models import User
from .serializers import UserSerializer
from .validate import *
from user.models import User
import jwt

class UserModelTestCase(TestCase):
    def setUp(self):
        User.objects.create(username='test-user',password='test-password',email='test_email@gmail.com',level='USER')

    def tearDown(self):
        User.objects.all().delete()

    def test_model_creation(self):
        user = User.objects.first()

        self.assertIsNotNone(user)
        self.assertEqual(user.username, 'test-user')
        self.assertEqual(user.email, 'test_email@gmail.com')

class UserApiTestCases(TestCase):
    def setUp(self):
        User.objects.create(username="user-01", password="pass-01", email="email_01@gmail.com", level="SUPERUSER")
        User.objects.create(username="user-02", password="pass-02", email="email_02@gmail.com", level="USER")
        User.objects.create(username="user-03", password="pass-03", email="email_03@gmail.com", level="ADMINISTRATOR")

    def tearDown(self):
        User.objects.all().delete()

    def test_get_users_success(self):
        user = User.objects.filter(username='user-01').first()
        token = jwt.encode({'id': user.id} , 'secret', algorithm='HS256')
        
        self.client.cookies['jwt'] = token.decode('utf-8')

        response = self.client.get(reverse("getUsers"))
        test_users = User.objects.all()
        serializer = UserSerializer(test_users, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(len(response.data), 3)
    
    def test_get_users_raiseErrorIfLevelIsUser(self):
        user = User.objects.filter(username='user-02').first()
        token = jwt.encode({'id': user.id} , 'secret', algorithm='HS256')
        
        self.client.cookies['jwt'] = token.decode('utf-8')

        with self.assertRaises(ValidationError):
            UserValidate.validateUserAccess(user.level)

    def test_add_user_success(self):
        user = User.objects.filter(username='user-01').first()
        
        token = jwt.encode({'id': user.id} , 'secret', algorithm='HS256')
        
        self.client.cookies['jwt'] = token.decode('utf-8')

        request = {
            "username": "johndoe",
            "password": "doe123",
            "email": "johndoe@gmail.com",
            "level": "user"
        }

        response = self.client.post(reverse('addUser'), data=request, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], request['username'])
        self.assertEqual(response.data['email'], request['email'])
        self.assertEqual(response.data['level'], request['level'])
        self.assertTrue(User.objects.filter(username='johndoe').exists())

    def test_add_user_raiseErrorIfLevelIsUser(self):
        user = User.objects.filter(username='user-02').first()
        token = jwt.encode({'id': user.id} , 'secret', algorithm='HS256')
        
        self.client.cookies['jwt'] = token.decode('utf-8')

        with self.assertRaises(ValidationError):
            UserValidate.validateUserAccess(user.level)

    def test_add_user_raiseErrorIfAValidationFails(self):
        user = User.objects.filter(username='user-02').first()
        token = jwt.encode({'id': user.id} , 'secret', algorithm='HS256')
    
        self.client.cookies['jwt'] = token.decode('utf-8')

        request = {
            "username": "johndoe",
            "password": "doe123",
            "email": "johndoegmail.com",
            "level": "user"
        }

        response = self.client.post(reverse('addUser'), data=request, format='json')

        with self.assertRaises(ValidationError):
            UserValidate.validateUsername(user.username, 'POST', None)
            UserValidate.validatePassword(user.username, 'POST', None)
            UserValidate.validateEmail(user.username, 'POST', None)
            UserValidate.validateLevel(user.username, 'POST', None)
    
    def test_edit_user_success(self):
        user = User.objects.filter(username='user-01').first()
        token = jwt.encode({'id': user.id} , 'secret', algorithm='HS256')
        
        self.client.cookies['jwt'] = token.decode('utf-8')

        createdUser = User.objects.create(username="create-user",password="create-123",email="created@gmail.com",level="ADMINISTRATOR")

        request = {
            "username": "createuser111",
            "password": "create123",
            "email": "created123@gmail.com",
            "level": "USER"
        }

        response = self.client.put(reverse('updateUser', args=[createdUser.id]), data=request, format='json', content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(User.objects.filter(username='createuser111').exists())
        
        updatedUser = User.objects.filter(username='createuser111').first()

        self.assertEqual(updatedUser.email, 'created123@gmail.com')
        self.assertEqual(updatedUser.level, 'USER')

    def test_delete_user_success(self):
        user = User.objects.filter(username='user-01').first()
        token = jwt.encode({'id': user.id} , 'secret', algorithm='HS256')
        
        self.client.cookies['jwt'] = token.decode('utf-8')

        createdUser = User.objects.create(username="create-user",password="create-123",email="created@gmail.com",level="ADMINISTRATOR")

        response = self.client.delete(reverse('deleteUser', args=[createdUser.id]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(User.objects.filter(username='create-user').first())
    
    def test_login_success(self):
        user = User.objects.filter(username='user-01').first()

        data = {
            "username": user.username,
            "password": user.password
        }

        response = self.client.post(reverse('login'), data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('jwt', response.cookies)
        self.assertIsNotNone(response.cookies['jwt'])

    def test_login_returnErrorMessageIfNoUserFound(self):
        user = User.objects.filter(username='user-01').first()
        token = jwt.encode({'id': user.id} , 'secret', algorithm='HS256')
        
        self.client.cookies['jwt'] = token.decode('utf-8')

        data = {
            "username": "anonymous",
            "password": "password123"
        }

        response = self.client.post(reverse('login'), data=data, format='json')

        self.assertEqual(response.data, {"message": "User not found"})
    
    def test_logout_success(self):
        user = User.objects.filter(username='user-01').first()

        data = {
            "username": user.username,
            "password": user.password
        }

        response = self.client.post(reverse('login'), data=data, format='json')
        response = self.client.post(reverse('logout'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.cookies['jwt'].value, '')
        self.assertEqual(response.data, {"message": "User logged out"})

    def test_logout_returnErrorMessageWhenNoUserLoggedIn(self):
        response = self.client.post(reverse('logout'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"error": "No user logged in"})


    
