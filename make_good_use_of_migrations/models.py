from django.db import models
from django.dispatch.dispatcher import receiver
from django.db.models.signals import pre_save


# Create your models here.

class Author(models.Model):
    name = models.CharField(max_length=32)


class Book(models.Model):
    name = models.CharField(max_length=32)
    author = models.ForeignKey(to=Author, on_delete=models.CASCADE, null=False)
    remark = models.CharField(max_length=32, null=True)

    def print_name(self):
        print(self.name)

    @classmethod
    def print_class_name(cls):
        print(cls.__name__)

    def save(self, *args, **kwargs):
        if not self.remark:
            self.remark = 'This is a book.'


@receiver(pre_save, sender=Book)
def generate_book_remark(sender, instance, *args, **kwargs):
    print(instance)
    if not instance.remark:
        instance.remark = 'This is a book.'
