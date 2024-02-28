from django.test import TestCase
from django.urls import reverse
from rest_framework_jwt.settings import api_settings
from rest_framework import status
from .models import Store, User
from .serializers import StoreSerializer
from .validate import *
from user.validate import UserValidate
import jwt, time, datetime

class StoreModelTestCase(TestCase):
    def setUp(self):
        owner = User.objects.create(username='test-user',password='test-password',email='test_email@gmail.com',level='USER')
        Store.objects.create(name='test-store',type='test-type',address='test-address',owner=owner)

    def tearDown(self):
        Store.objects.all().delete()
        User.objects.all().delete()

    def test_model_creation(self):
        store = Store.objects.first()
        owner = User.objects.first()

        self.assertIsNotNone(store)
        self.assertEqual(store.name, 'test-store')
        self.assertEqual(store.address, 'test-address')
        self.assertEqual(store.owner, owner)

class StoreApiTestCases(TestCase):
    def setUp(self):
        owner_1 = User.objects.create(username='test-owner-1',password='test-password',email='test_email_1@gmail.com',level='ADMINISTRATOR')
        owner_2 = User.objects.create(username='test-owner-2',password='test-password',email='test_email_2@gmail.com',level='USER')

        Store.objects.create(name="Nike", type="Shoes", address="address_1@gmail.com", owner=owner_1)
        Store.objects.create(name="Adidas", type="Shoes", address="address_2@gmail.com", owner=owner_1)
        Store.objects.create(name="Samgyup", type="Food", address="address_3@gmail.com", owner=owner_2)
        Store.objects.create(name="Puregold", type="Grocery", address="address_4@gmail.com", owner=owner_2)
    
    def tearDown(self):
        Store.objects.all().delete()
        User.objects.all().delete()

    def test_get_stores_success(self):
        user = User.objects.filter(username='test-owner-1').first()
        token = jwt.encode({'id': user.id} , 'secret', algorithm='HS256')
        
        self.client.cookies['jwt'] = token.decode('utf-8')

        response = self.client.get(reverse("getStores"))
        test_stores = Store.objects.all()
        serializer = StoreSerializer(test_stores, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(len(response.data), 4)

    def test_get_stores_raiseErrorIfLevelIsUser(self):
        user = User.objects.filter(username='test-owner-2').first()
        token = jwt.encode({'id': user.id} , 'secret', algorithm='HS256')
        
        self.client.cookies['jwt'] = token.decode('utf-8')

        with self.assertRaises(ValidationError):
            UserValidate.validateUserAccess(user.level)

    def test_get_storeDetails_success(self):
        user = User.objects.filter(username='test-owner-1').first()
        store = Store.objects.filter(name='Nike').first()

        token = jwt.encode({'id': user.id} , 'secret', algorithm='HS256')
        
        self.client.cookies['jwt'] = token.decode('utf-8')

        response = self.client.get(reverse("getStoreDetails", args=[store.id]))
        test_store = store
        serializer = StoreSerializer(test_store)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.data.get('name', None), 'Nike')

    def test_get_storeDetails_raiseErrorIfStoreDoesNotExists(self):
        user = User.objects.filter(username='test-owner-1').first()
        store = Store.objects.filter(name='Nike').first()

        token = jwt.encode({'id': user.id} , 'secret', algorithm='HS256')
        
        self.client.cookies['jwt'] = token.decode('utf-8')

        response = self.client.get(reverse("getStoreDetails", args=[5]))

        self.assertEqual(response.data, "error: ['Store does not exists']")

    def test_get_storeDetails_raiseErrorIfUserHasNoPermission(self):
        user = User.objects.filter(username='test-owner-2').first()
        store = Store.objects.filter(name='Nike').first()

        token = jwt.encode({'id': user.id} , 'secret', algorithm='HS256')
        
        self.client.cookies['jwt'] = token.decode('utf-8')

        response = self.client.get(reverse("getStoreDetails", args=[store.id]))

        self.assertEqual(response.data, 'error: ["You don\'t have the permission to view other stores"]')

    def test_add_store_success(self):
        user = User.objects.filter(username='test-owner-2').first()

        token = jwt.encode({'id': user.id} , 'secret', algorithm='HS256')
        
        self.client.cookies['jwt'] = token.decode('utf-8')

        request = {
            "name": "test-store",
            "type": "test-type",
            "address": "test-store-address",
            "owner": user
        }

        response = self.client.post(reverse("addStore"), data=request, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.content, b'{"message":"Store test-store owned by test-owner-2 created"}')
        self.assertTrue(Store.objects.filter(name='test-store').exists())

    def test_edit_store_success(self):
        user = User.objects.filter(username='test-owner-1').first()
        store = Store.objects.filter(name='Nike').first()

        token = jwt.encode({'id': user.id} , 'secret', algorithm='HS256')
        
        self.client.cookies['jwt'] = token.decode('utf-8')

        request = {
            "name": "test-store111",
            "type": "test-type111",
            "address": "test-store-address111",
            "owner": user.id
        }

        response = self.client.put(reverse('updateStore', args=[store.id]), data=request, format='json', content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(Store.objects.filter(name='test-store111').exists())
        
        updatedStore = Store.objects.filter(name='test-store111').first()

        self.assertEqual(updatedStore.address, 'test-store-address111')
        self.assertEqual(updatedStore.owner, user)

    def test_edit_store_raiseErrorWhenUserUpdateUnownedStore(self):
            user = User.objects.filter(username='test-owner-2').first()
            store = Store.objects.filter(name='Nike').first()

            token = jwt.encode({'id': user.id} , 'secret', algorithm='HS256')
            
            self.client.cookies['jwt'] = token.decode('utf-8')

            request = {
                "name": "test-store111",
                "type": "test-type111",
                "address": "test-store-address111",
                "owner": user.id
            }

            response = self.client.put(reverse('updateStore', args=[store.id]), data=request, format='json', content_type='application/json')

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.content, b'"error: [\\"You don\'t have the permission to edit other stores\\"]"') 

    def test_edit_store_raiseErrorIfStoreDoesNotExists(self):
        user = User.objects.filter(username='test-owner-2').first()
        store = Store.objects.filter(name='Nike').first()

        token = jwt.encode({'id': user.id} , 'secret', algorithm='HS256')
        
        self.client.cookies['jwt'] = token.decode('utf-8')

        request = {
            "name": "test-store111",
            "type": "test-type111",
            "address": "test-store-address111",
            "owner": user.id
        }

        response = self.client.put(reverse('updateStore', args=[6]), data=request, format='json', content_type='application/json')

        self.assertEqual(response.data, "error: ['Store not found']")

    def test_delete_store_success(self):
        user = User.objects.filter(username='test-owner-2').first()

        token = jwt.encode({'id': user.id} , 'secret', algorithm='HS256')
        
        self.client.cookies['jwt'] = token.decode('utf-8')

        createdStore = Store.objects.create(name="delete-store", type='delete-type', address='delete ave', owner=user)

        self.assertIsNotNone(Store.objects.filter(name='delete-store').first())

        response = self.client.delete(reverse('deleteStore', args=[createdStore.id]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(Store.objects.filter(name='delete-store').first())