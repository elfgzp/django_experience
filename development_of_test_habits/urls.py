# -*- coding: utf-8 -*-
__author__ = 'gzp'

from django.urls import path
from development_of_test_habits import views

urlpatterns = [
    path('hello_test_case', views.HelloTestCase.as_view(), name='hello_test_case'),
]
