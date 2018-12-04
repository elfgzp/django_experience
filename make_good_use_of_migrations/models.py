from django.db import models


# Create your models here.

class Author(models.Model):
    name = models.CharField(max_length=32)


class Book(models.Model):
    name = models.CharField(max_length=32)
    author = models.ForeignKey(to=Author, on_delete=models.CASCADE, null=False)
    remark = models.CharField(max_length=32, null=True)
