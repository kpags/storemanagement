from django.db import models

class User(models.Model):
    username =  models.CharField(max_length=20)
    password = models.CharField(max_length=20)
    email = models.CharField(max_length=500)
    level = models.CharField(max_length=100)

    def __str__(self):
        return self.username
    
    def return_secret_key():
        return 'de58d24a-32e2-4ae5-a07b-f86965d83bb9'
