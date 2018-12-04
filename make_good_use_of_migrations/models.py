from django.db import models

# Create your models here.


class Book(models.Model):
    name = models.CharField(max_length=32)
    remark = models.CharField(max_length=32, null=True)
