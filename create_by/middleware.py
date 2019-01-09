# -*- coding: utf-8 -*-
__author__ = 'gzp'

from django import conf
from django.db.models import signals
from django.core.exceptions import FieldDoesNotExist
from django.utils.deprecation import MiddlewareMixin
from django.utils.functional import curry


class WhoDidMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.method not in ('GET', 'HEAD', 'OPTIONS', 'TRACE'):
            if hasattr(request, 'user') and request.user.is_authenticated:
                user = request.user
            else:
                user = None

            mark_whodid = curry(self.mark_whodid, user)
            signals.pre_save.connect(mark_whodid, dispatch_uid=(self.__class__, request,), weak=False)

    def process_response(self, request, response):
        if request.method not in ('GET', 'HEAD', 'OPTIONS', 'TRACE'):
            signals.pre_save.disconnect(dispatch_uid=(self.__class__, request,))
        return response

    def mark_whodid(self, user, sender, instance, **kwargs):
        create_by_field, update_by_field = conf.settings.CREATE_BY_FIELD, conf.settings.UPDATE_BY_FIELD

        try:
            instance._meta.get_field(create_by_field)
        except FieldDoesNotExist:
            pass
        else:
            if not getattr(instance, create_by_field):
                setattr(instance, create_by_field, user)

        try:
            instance._meta.get_field(update_by_field)
        except FieldDoesNotExist:
            pass
        else:
            setattr(instance, update_by_field, user)
