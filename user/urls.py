from django.urls import path, include
from . import views
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('getUsers/', views.getUsers, name='getUsers'),
    path('addUser/', views.addUser, name='addUser'),
    path('updateUser/<int:id>/', views.updateUser, name='updateUser'),
    path('deleteUser/<int:id>/', views.deleteUser, name='deleteUser'),
    path('login/', views.login, name="login"),
    path('logout/', views.logout, name="logout"),
    path('getJWT/', views.getJWT, name="getJWT")
]