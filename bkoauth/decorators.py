# -*- coding: utf-8 -*-
from functools import wraps

from django.utils.decorators import available_attrs

from .jwt_client import JWTClient, jwt_invalid_view


def apigw_required(view_func):
    """apigw装饰器
    """

    @wraps(view_func, assigned=available_attrs(view_func))
    def _wrapped_view(request, *args, **kwargs):
        request.jwt = JWTClient(request)
        if not request.jwt.is_valid:
            return jwt_invalid_view(request)
        return view_func(request, *args, **kwargs)

    return _wrapped_view
