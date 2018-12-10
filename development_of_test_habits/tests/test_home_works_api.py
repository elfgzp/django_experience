# -*- coding: utf-8 -*-
__author__ = 'gzp'

from django.test import TestCase
from django.urls import reverse

from django.contrib.auth.models import User

from mixer.backend.django import mixer

from development_of_test_habits import models


class HomeWorkAPITestCase(TestCase):
    def setUp(self):
        self.user = mixer.blend(User)

        self.random_home_works = [
            mixer.blend(models.HomeWork)
            for _ in range(11)
        ]

    def test_home_works_list_api(self):
        url = reverse('home_works_list')

        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

        self.client.force_login(self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), len(self.random_home_works))

        data_fields = [key for key in data[0].keys()]

        self.assertIn('school_name', data_fields)
        self.assertIn('class_name', data_fields)
        self.assertIn('student_name', data_fields)
        self.assertIn('name', data_fields)


