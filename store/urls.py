from django.urls import path, include
from . import views

urlpatterns = [
    path('getStores/', views.getStores, name="getStores"),
    path('getStoreDetails/<int:id>/', views.getStoreDetails, name="getStoreDetails"),
    path('getUserStores/', views.getUserStores, name="getUserStores"),
    path('addStore/', views.addStore, name="addStore"),
    path('updateStore/<int:id>/', views.updateStore, name='updateStore'),
    path('deleteStore/<int:id>/', views.deleteStore, name='deleteStore')
]