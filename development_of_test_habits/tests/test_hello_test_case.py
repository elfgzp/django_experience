# -*- coding: utf-8 -*-
__author__ = 'gzp'

from django.urls import resolve, reverse
from django.test import TestCase


class HelloTestCase(TestCase):
    def setUp(self):
        self.name = 'Django'

    def test_hello_test_case(self):
        url = '/test_case/hello_test_case'
        # url = reverse('hello_test_case')
        # Input: print(resolve(url))
        # Output: ResolverMatch(func=development_of_test_habits.views.hello_test_case.HelloTestCase, args=(), kwargs={}, url_name=hello_test_case, app_names=[], namespaces=[])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['msg'], 'Hello , I am a test Case')

        response = self.client.get(url, {'name': self.name})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['msg'], 'Hello Django I am a test Case')

