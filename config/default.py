# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸 (Blueking) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at https://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.
"""
import importlib

from blueapps.conf.default_settings import *  # noqa
from blueapps.conf.log import get_logging_config_dict
from pipeline.celery.settings import *  # noqa
from pipeline.eri.celery import queues
from celery import Celery

# pipeline 配置
from pipeline.celery.settings import *


CELERY_QUEUES.extend(queues.CELERY_QUEUES)  # 向 broker 队列中添加 bamboo-engine 专用队列

app = Celery("proj")

app.config_from_object("django.conf:settings")
# 请在这里加入你的自定义 APP
INSTALLED_APPS += (
    "apps.gsekit",
    "apps.iam",
    "drf_yasg",
    "rest_framework",
    # pipeline
    "pipeline",
    "pipeline.log",
    "pipeline.engine",
    "pipeline.component_framework",
    "pipeline.django_signal_valve",
    "pipeline.eri",
)

# 自定义中间件
MIDDLEWARE += (
    "blueapps.account.middlewares.BkJwtLoginRequiredMiddleware",
    "apps.middlewares.CommonMid",
    "apps.middlewares.UserLocalMiddleware",
)


# ===============================================================================
# Authentication
# ===============================================================================
AUTHENTICATION_BACKENDS += ("blueapps.account.backends.BkJwtBackend",)

# 所有环境的日志级别可以在这里配置
# LOG_LEVEL = 'INFO'

#
# 静态资源文件(js,css等）在APP上线更新后, 由于浏览器有缓存,
# 可能会造成没更新的情况. 所以在引用静态资源的地方，都把这个加上
# Django 模板中：<script src="/a.js?v={{ STATIC_VERSION }}"></script>
# mako 模板中：<script src="/a.js?v=${ STATIC_VERSION }"></script>
# 如果静态资源修改了以后，上线前改这个版本号即可
#
STATIC_VERSION = "1.0"

STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]

# CELERY 开关，使用时请改为 True，修改项目目录下的 Procfile 文件，添加以下两行命令：
# worker: python manage.py celery worker -l info
# beat: python manage.py celery beat -l info
# 不使用时，请修改为 False，并删除项目目录下的 Procfile 文件中 celery 配置
IS_USE_CELERY = True

# CELERY 并发数，默认为 2，可以通过环境变量或者 Procfile 设置
CELERYD_CONCURRENCY = os.getenv("BK_CELERYD_CONCURRENCY", 2)

# CELERY 配置，申明任务的文件路径，即包含有 @task 装饰器的函数文件
CELERY_IMPORTS = (
    "apps.gsekit",
    "apps.gsekit.periodic_tasks.sync_process",
)


# load logging settings
LOGGING = get_logging_config_dict(locals())

# 初始化管理员列表，列表中的人员将拥有预发布环境和正式环境的管理员权限
# 注意：请在首次提测和上线前修改，之后的修改将不会生效
INIT_SUPERUSER = [
    "admin",
]

# 使用mako模板时，默认打开的过滤器：h(过滤html)
MAKO_DEFAULT_FILTERS = ["h"]

# BKUI是否使用了history模式
IS_BKUI_HISTORY_MODE = False

# 是否需要对AJAX弹窗登录强行打开
IS_AJAX_PLAIN_MODE = False

# 国际化配置
LOCALE_PATHS = (os.path.join(BASE_DIR, "locale"),)

USE_TZ = True
TIME_ZONE = "Asia/Shanghai"
LANGUAGE_CODE = "zh-hans"

LANGUAGES = (
    ("en", "English"),
    ("zh-hans", "简体中文"),
)

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

"""
以下为框架代码 请勿修改
"""
# celery settings
if IS_USE_CELERY:

    INSTALLED_APPS = locals().get("INSTALLED_APPS", [])
    INSTALLED_APPS += ("django_celery_beat", "django_celery_results")
    CELERY_ENABLE_UTC = False
    CELERYBEAT_SCHEDULER = "django_celery_beat.schedulers.DatabaseScheduler"

# remove disabled apps
if locals().get("DISABLED_APPS"):
    INSTALLED_APPS = locals().get("INSTALLED_APPS", [])
    DISABLED_APPS = locals().get("DISABLED_APPS", [])

    INSTALLED_APPS = [_app for _app in INSTALLED_APPS if _app not in DISABLED_APPS]

    _keys = (
        "AUTHENTICATION_BACKENDS",
        "DATABASE_ROUTERS",
        "FILE_UPLOAD_HANDLERS",
        "MIDDLEWARE",
        "PASSWORD_HASHERS",
        "TEMPLATE_LOADERS",
        "STATICFILES_FINDERS",
        "TEMPLATE_CONTEXT_PROCESSORS",
    )

    import itertools

    for _app, _key in itertools.product(DISABLED_APPS, _keys):
        if locals().get(_key) is None:
            continue
        locals()[_key] = tuple([_item for _item in locals()[_key] if not _item.startswith(_app + ".")])

DEBUG = False
CONF_PATH = os.path.abspath(__file__)
PROJECT_ROOT = os.path.dirname(os.path.dirname(CONF_PATH))
# ==============================================================================
# Templates
# ==============================================================================
# mako template dir

MAKO_TEMPLATE_DIR = [os.path.join(PROJECT_ROOT, directory) for directory in ["static/dist", "templates"]]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(PROJECT_ROOT, "templates"), os.path.join(PROJECT_ROOT, "static/")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "blueapps.template.context_processors.blue_settings",
                "common.context_processors.mysetting",  # 自定义模版context，可在页面中使用STATIC_URL等变量
            ],
            "debug": DEBUG,
        },
    },
]

# ===============================================================================
# 项目配置
# ===============================================================================
BK_PAAS_HOST = os.environ.get("BK_PAAS_HOST", "")
BK_PAAS_INNER_HOST = os.environ.get("BK_PAAS_INNER_HOST", BK_PAAS_HOST)
BK_CC_HOST = os.environ.get("BK_CC_HOST", BK_PAAS_HOST.replace("paas", "cmdb"))
BK_SAAS_HOST = os.environ.get("BK_SAAS_HOST", f"{BK_PAAS_HOST}/o/{APP_CODE}/")

BK_ADMIN_USERNAME = os.getenv("BKAPP_ADMIN_USERNAME", "admin")

# 敏感参数,记录请求参数时需剔除
SENSITIVE_PARAMS = ["app_code", "app_secret", "bk_app_code", "bk_app_secret", "auth_info"]

# rest_framework
REST_FRAMEWORK = {
    "DATETIME_FORMAT": "%Y-%m-%d %H:%M:%S",
    # "EXCEPTION_HANDLER": "apps.generic.custom_exception_handler",
    "DEFAULT_RENDERER_CLASSES": ("rest_framework.renderers.JSONRenderer",),
}

# 并发请求数
CONCURRENT_NUMBER = int(os.getenv("BKAPP_CONCURRENT_NUMBER", 50))

# 适配类型
ADAPTER_TYPE = os.getenv("BKAPP_ADAPTER_TYPE", "base")

# ==============================================================================
# IAM
# ==============================================================================

# 使用权限中心
USE_IAM = bool(os.getenv("BKAPP_USE_IAM", False))

if not USE_IAM:
    iam_idx = INSTALLED_APPS.index("apps.iam")
    INSTALLED_APPS = INSTALLED_APPS[:iam_idx] + INSTALLED_APPS[iam_idx + 1 :]

BK_IAM_SYSTEM_ID = "bk_gsekit"
BK_IAM_SYSTEM_NAME = "GSEKIT"
BK_IAM_MIGRATION_APP_NAME = "iam"
BK_IAM_SKIP = False

BK_IAM_INNER_HOST = os.getenv("BK_IAM_V3_INNER_HOST", "http://bkiam.service.consul")

# BK_IAM_RESOURCE_API_HOST = os.getenv("BKAPP_IAM_RESOURCE_API_HOST", f"{BK_PAAS_HOST}/o/{APP_CODE}/")
BK_IAM_RESOURCE_API_HOST = os.getenv("BKAPP_IAM_RESOURCE_API_HOST", f"{BK_PAAS_INNER_HOST}/o/{APP_CODE}/")

# 权限中心 SaaS host
BK_IAM_APP_CODE = os.getenv("BKAPP_IAM_V3_APP_CODE", "bk_iam")
BK_IAM_SAAS_HOST = os.environ.get("BKAPP_IAM_V3_SAAS_HOST", f"{BK_PAAS_HOST}/o/{BK_IAM_APP_CODE}/")

# TAM
TAM_AEGIS_KEY = os.getenv("BKAPP_TAM_AEGIS_KEY")
TAM_AEGIS_URL = os.getenv("BKAPP_TAM_AEGIS_URL")

# ==============================================================================
# Cache
# ==============================================================================

CACHES["default"] = {
    "BACKEND": "django.core.cache.backends.db.DatabaseCache",
    "LOCATION": "django_cache",
    "OPTIONS": {"MAX_ENTRIES": 10000, "CULL_FREQUENCY": 10},
}
