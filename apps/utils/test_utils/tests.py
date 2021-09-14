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
import os
import json
from uuid import uuid4
from typing import List

import urllib3
from mock import patch, MagicMock
from django.conf import settings
from django.test import Client, TestCase
from django.utils.deprecation import MiddlewareMixin

from apps.utils.test_utils.swagger_tests import SwaggerViewSetTestMetaClass
from apps.utils.local import activate_request, set_local_param, _local

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

JSON_CONTENT = "application/json"
PAAS_USERNAME = os.environ.get("PAAS_ADMIN_USER")
PAAS_PASSWORD = os.environ.get("PAAS_ADMIN_PASS")
BK_TICKET = os.environ.get("BK_TICKET")
BK_USERNAME = os.environ.get("BK_USERNAME", "admin")


class MyTestClient(Client):
    @staticmethod
    def check_environ():
        to_check_var = [
            "APP_CODE",
            "APP_TOKEN",
            "BK_PAAS_HOST",
            "PAAS_ADMIN_USER",
            "PAAS_ADMIN_PASS",
        ]
        for var in to_check_var:
            if not os.environ.get(var):
                raise NotImplementedError(f"环境变量{var}未设置")

    @staticmethod
    def assert_response(response):
        """
        断言请求是否正确返回
        :param response:
        :return: 返回数据中的data字段
        """
        assert response.status_code == 200
        json_response = json.loads(response.content)
        try:
            assert json_response.get("result")
        except AssertionError as error:
            print("[RESPONSE ERROR]:%s" % response.content)
            raise error

        return json_response["data"]

    @staticmethod
    def transform_data(data, content_type=JSON_CONTENT):
        """
        根据content_type转化请求参数
        :param data:
        :param content_type:
        :return:
        """
        if content_type == JSON_CONTENT:
            data = json.dumps(data)
        return data

    def get(self, path, data=None, secure=True, **extra):
        response = super(MyTestClient, self).get(path, data=data, secure=secure, **extra)

        return self.assert_response(response)

    def post(
        self,
        path,
        data=None,
        content_type=JSON_CONTENT,
        follow=False,
        secure=True,
        **extra,
    ):
        data = self.transform_data(data, content_type)
        response = super(MyTestClient, self).post(
            path,
            data=data,
            content_type=JSON_CONTENT,
            follow=follow,
            secure=secure,
            **extra,
        )
        return self.assert_response(response)

    def patch(
        self,
        path,
        data=None,
        content_type=JSON_CONTENT,
        follow=False,
        secure=True,
        **extra,
    ):
        data = self.transform_data(data, content_type)
        response = super(MyTestClient, self).patch(
            path,
            data=data,
            content_type=JSON_CONTENT,
            follow=follow,
            secure=secure,
            **extra,
        )
        return self.assert_response(response)

    def put(
        self,
        path,
        data=None,
        content_type=JSON_CONTENT,
        follow=False,
        secure=True,
        **extra,
    ):
        data = self.transform_data(data, content_type)
        response = super(MyTestClient, self).put(
            path,
            data=data,
            content_type=JSON_CONTENT,
            follow=follow,
            secure=secure,
            **extra,
        )
        return self.assert_response(response)

    def delete(
        self,
        path,
        data=None,
        content_type=JSON_CONTENT,
        follow=False,
        secure=True,
        **extra,
    ):
        data = self.transform_data(data, content_type)
        response = super(MyTestClient, self).delete(
            path,
            data=data,
            content_type=JSON_CONTENT,
            follow=follow,
            secure=secure,
            **extra,
        )
        return self.assert_response(response)


class MyTestCase(TestCase, metaclass=SwaggerViewSetTestMetaClass):
    # None表示展示全量断言差异
    maxDiff = None

    client_class = MyTestClient
    client = MyTestClient()

    # 默认的测试业务
    bk_biz_id = 1

    # swagger文档自动化测试相关
    # 不为None时，自动生成并执行指定viewset接口单测
    swagger_test_view = None
    path_params = {"bk_biz_id": bk_biz_id}
    fields_exempt = ["created_at", "updated_at"]
    actions_exempt = []

    # 断言相关
    recursion_type = [dict, list]
    string_type = [str]

    def remove_keys(self, data, keys: List[str]) -> None:
        children = []
        if isinstance(data, dict):
            for key in keys:
                data.pop(key, None)
            children = data.values()
        elif isinstance(data, list):
            children = data
        for child_data in children:
            if type(child_data) in self.recursion_type:
                self.remove_keys(child_data, keys)
        return

    def assertExemptDataStructure(self, result_data, expected_data, value_eq=False, list_exempt=False, is_sort=True):
        self.remove_keys(result_data, self.fields_exempt)
        self.remove_keys(expected_data, self.fields_exempt)
        return self.assertDataStructure(result_data, expected_data, value_eq, list_exempt=list_exempt, is_sort=is_sort)

    def assertDataStructure(self, result_data, expected_data, value_eq=False, list_exempt=False, is_sort=True):
        """
        将数据的结构以及类型进行断言验证
        :param result_data: 后台返回的数据
        :param expected_data: 希望得到的数据
        :param value_eq: 是否对比值相等
        :param list_exempt: 是否豁免列表的比对
        :param is_sort: 是否对列表（子列表）在对比前排序
        """
        result_data_type = type(result_data)

        # 判断类型是否一致
        self.assertEqual(result_data_type, type(expected_data))

        # 判断类型是否为字典
        if result_data_type is dict:
            # 將传入的预给定信息，将键值分别取出
            for expected_key, expected_value in list(expected_data.items()):
                # 判断键是否存在
                self.assertTrue(
                    expected_key in list(result_data.keys()),
                    msg="key:[%s] is expected" % expected_key,
                )

                result_value = result_data[expected_key]

                # 返回None时忽略 @todo一刀切需要调整
                if expected_value is None or result_value is None:
                    return

                # 取出后台返回的数据result_data，判断是否与给定的类型相符
                result_value_type = type(result_value)
                expected_value_type = type(expected_value)
                self.assertEqual(
                    result_value_type,
                    expected_value_type,
                    msg="type error! Expect [%s] to be [%s], but got [%s]"
                    % (expected_key, expected_value_type, result_value_type),
                )

                if value_eq:
                    self.assertEqual(result_value, expected_value)

                # 判断该类型是否为字典或者列表
                if expected_value_type in self.recursion_type:
                    # 进行递归
                    self.assertDataStructure(
                        result_value, expected_value, value_eq=value_eq, list_exempt=list_exempt, is_sort=is_sort
                    )

        #  判断类型是否为列表
        elif result_data_type is list:
            # 列表不为空且不进行列表比对的豁免
            if not list_exempt:

                if value_eq:
                    # 比对列表内的值是否相等
                    self.assertListEqual(result_data, expected_data, is_sort=is_sort)
                else:
                    # 否则认为列表里所有元素的数据结构都是一致的
                    _expected_data = expected_data[0]
                    for _data in result_data:
                        if type(_data) in self.recursion_type:
                            self.assertDataStructure(
                                _data, _expected_data, value_eq=value_eq, list_exempt=list_exempt, is_sort=is_sort
                            )

        # 判断值是否一致
        elif value_eq:
            self.assertEqual(result_data, expected_data)

    def assertListEqual(self, list1, list2, msg=None, is_sort=False):
        if is_sort:
            list1 = sorted([json.dumps(item, sort_keys=True) for item in list1])
            list2 = sorted([json.dumps(item, sort_keys=True) for item in list2])
        super(MyTestCase, self).assertListEqual(list1, list2, msg=msg)

    def setUp(self) -> None:
        """执行TestCase内test时调用一次"""
        super(MyTestCase, self).setUp()

    def tearDown(self) -> None:
        """执行TestCase内test后调用一次"""
        super(MyTestCase, self).tearDown()

    @classmethod
    def setUpTestData(cls):
        """TestCase实例生成时调用一次, 可DB回滚
        该hook比setUpClass先执行，需要考虑mock相关顺序
        """
        super().setUpTestData()

        patch("apps.api.utils.params.get_request", MagicMock(return_value=MOCK_REQUEST_OBJECT)).start()
        patch("apps.api.base.get_request", MagicMock(return_value=MOCK_REQUEST_OBJECT)).start()
        patch("apps.utils.batch_request.get_request", MagicMock(return_value=MOCK_REQUEST_OBJECT)).start()
        patch("apps.utils.local.get_request", MagicMock(return_value=MOCK_REQUEST_OBJECT)).start()

    @classmethod
    def setUpClass(cls):
        """TestCase实例生成时调用一次"""
        super(MyTestCase, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        """TestCase实例销毁时调用一次"""
        super(MyTestCase, cls).tearDownClass()
        patch.stopall()


class ObjectBase(object):
    META = {}
    COOKIES = {}


MOCK_REQUEST_OBJECT = ObjectBase()
MOCK_REQUEST_OBJECT.request_id = uuid4().hex
MOCK_REQUEST_OBJECT.user = ObjectBase()
MOCK_REQUEST_OBJECT.user.username = BK_USERNAME
MOCK_REQUEST_OBJECT.user.is_superuser = True
MOCK_REQUEST_OBJECT.user.is_active = True
MOCK_REQUEST_OBJECT.user.is_authenticated = True
MOCK_REQUEST_OBJECT.permission_exempt = True
MOCK_REQUEST_OBJECT.META.update({"HTTP_X_REQUESTED_WITH": "XMLHttpRequest"})
MOCK_REQUEST_OBJECT.COOKIES["bk_ticket"] = BK_TICKET
MOCK_REQUEST_OBJECT.headers = {}


class OverrideMiddleware(MiddlewareMixin):
    def process_request(self, request):
        _local.request = MOCK_REQUEST_OBJECT
        activate_request(_local.request)
        set_local_param("time_zone", settings.TIME_ZONE)

        class Base(object):
            pass

        request.user = Base()
        request.user.username = "admin"
        request.user.nickname = "admin"
        request.user.is_superuser = True
        request.user.is_authenticated = True
        request.user.is_active = True
        request.permission_exempt = True
        request.user.is_anonymous = False
        request.user.avatar_url = None
        request.META.update({"HTTP_X_REQUESTED_WITH": "XMLHttpRequest"})


def patch_get_request(wrap_func):
    """mock get_request return"""

    def func(*args, **kwargs):
        patch("apps.api.utils.params.get_request", MagicMock(return_value=MOCK_REQUEST_OBJECT)).start()
        patch("apps.api.base.get_request", MagicMock(return_value=MOCK_REQUEST_OBJECT)).start()
        patch("apps.utils.batch_request.get_request", MagicMock(return_value=MOCK_REQUEST_OBJECT)).start()
        patch("apps.utils.local.get_request", MagicMock(return_value=MOCK_REQUEST_OBJECT)).start()
        return wrap_func(*args, **kwargs)

    return func


OVERRIDE_MIDDLEWARE = "apps.utils.tests.OverrideMiddleware"
