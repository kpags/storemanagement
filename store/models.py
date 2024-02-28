from django.db import models
from user.models import User

class Store(models.Model):
    name =  models.CharField(max_length=500)
    type = models.CharField(max_length=20)
    address = models.CharField(max_length=500)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=False)

    def __str__(self):
        return self.name
        

