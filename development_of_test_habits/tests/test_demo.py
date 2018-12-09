# -*- coding: utf-8 -*-
__author__ = 'gzp'

from django.test import TestCase


class Demo(TestCase):
    def setUp(self):
        print('setUp')

    def tearDown(self):
        print('tearDown')

    def test_demo(self):
        print('test_demo')

    def test_demo_2(self):
        print('test_demo2')

