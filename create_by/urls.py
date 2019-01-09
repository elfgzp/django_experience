# -*- coding: utf-8 -*-
__author__ = 'gzp'

from django.urls import include, path

from rest_framework.routers import DefaultRouter

from .views import AuthorViewSet, BookViewSet

router = DefaultRouter(trailing_slash=False)

router.register('books', BookViewSet, base_name='book')
router.register('authors', AuthorViewSet, base_name='author')

urlpatterns = [
    path('api/', include(router.urls))
]

