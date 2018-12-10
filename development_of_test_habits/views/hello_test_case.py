# -*- coding: utf-8 -*-
__author__ = 'gzp'

from rest_framework.views import APIView
from rest_framework.response import Response


class HelloTestCase(APIView):
    def get(self, request, *args, **kwargs):
        data = {
            'msg': 'Hello %s I am a test Case' % request.query_params.get('name', ',')
        }
        test_header = request.META.get('HTTP_TEST_HEADER')
        if test_header:
            data['test_header'] = test_header
        return Response(data)
