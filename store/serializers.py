from rest_framework import serializers
from .models import Store
from user.models import User

class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = '__all__'