from django.db import models

from django import conf


class Author(models.Model):
    name = models.CharField(max_length=32)
    create_by = models.ForeignKey(conf.settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
                                  related_name='%(class)s_create_by_user')
    update_by = models.ForeignKey(conf.settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
                                  related_name='%(class)s_update_by_user')


class Book(models.Model):
    author_id = models.ForeignKey(Author, on_delete=models.CASCADE)

    name = models.CharField(max_length=32)
    create_by = models.ForeignKey(conf.settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
                                  related_name='%(class)s_create_by_user')
    update_by = models.ForeignKey(conf.settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
                                  related_name='%(class)s_update_by_user')
