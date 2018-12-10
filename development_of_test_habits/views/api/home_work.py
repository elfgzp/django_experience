# -*- coding: utf-8 -*-
__author__ = 'gzp'

from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.permissions import IsAuthenticated

from development_of_test_habits.models import HomeWork
from development_of_test_habits.serializers import HomeWorkSerializer


class HomeWorkViewSet(ReadOnlyModelViewSet):
    queryset = HomeWork.objects.all()
    serializer_class = HomeWorkSerializer
    permission_classes = (IsAuthenticated, )


