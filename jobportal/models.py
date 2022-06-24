import uuid
from djongo import models
from django.contrib.auth.models import User

# Create your models here.
class ISCO(models.Model):
    _id = models.ObjectIdField()
    Group = models.TextField()
    Name = models.TextField()
    Description = models.TextField()

class JobAnalysis(models.Model):
    _id = models.ObjectIdField()
    Career = models.TextField()
    HardSkill = models.TextField()
    SoftSkill = models.TextField()
    Personality = models.TextField()

class MyUser(models.Model):
    _id = models.ObjectIdField()
    user = models.CharField(max_length=200, null=True)
    email = models.EmailField(max_length=200, null=True)
    Firstname = models.CharField(max_length=200, null=True)
    Lastname = models.CharField(max_length=200, null=True)
    skill = models.CharField(max_length=500, null=True)

    def __str__(self):
        return self.user