# -*- coding: utf-8 -*-
"""Django project settings
"""


try:
    from django.conf import settings

    APP_CODE = settings.APP_ID
    SECRET_KEY = settings.APP_TOKEN
    COMPONENT_SYSTEM_HOST = settings.BK_COMPONENT_API_URL
    DEFAULT_BK_API_VER = getattr(settings, "DEFAULT_BK_API_VER", "v2")
except Exception:
    APP_CODE = ""
    SECRET_KEY = ""
    COMPONENT_SYSTEM_HOST = ""
    DEFAULT_BK_API_VER = "v2"

CLIENT_ENABLE_SIGNATURE = False
