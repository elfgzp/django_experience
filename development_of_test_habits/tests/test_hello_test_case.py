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
        self.assertEqual(response.status_code, 200)  # 期望的Http相应码为200
        data = response.json()
        self.assertEqual(data['msg'], 'Hello , I am a test Case')  # 期望的msg返回结果为'Hello , I am a test Case'

        response = self.client.get(url, {'name': self.name})
        self.assertEqual(response.status_code, 200)  # 期望的Http相应码为200
        data = response.json()
        self.assertEqual(data['msg'], 'Hello Django I am a test Case')  # 期望的msg返回结果为'Hello Django I am a test Case'

        # 假设我们要在接口中增加请求头'TEST_HEADER'
        # 则在测试时需要加上前缀'HTTP_'最终的结果为'HTTP_TEST_HEADER'
        response = self.client.get(url, **{'HTTP_TEST_HEADER': 'This is a test header.'})
        data = response.json()
        self.assertEqual(data['test_header'], 'This is a test header.')
