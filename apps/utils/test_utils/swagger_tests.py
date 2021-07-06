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
import sys
import json
import inspect
from functools import wraps
from typing import List, Dict, Tuple

from rest_framework import status
from django.test import override_settings
from drf_spectacular.generators import EndpointEnumerator

OVERRIDE_MIDDLEWARE = "apps.utils.test_utils.tests.OverrideMiddleware"


class EndPointIndex:
    PATH = 0
    PATTERN = 1
    METHOD = 2
    ACTION_FUNC = 3


class ActionFuncIndex:
    # action指定url_path时方法名称不为path
    FUNC_NAME = 0
    FUNC = 1


class Action:
    def __init__(self, request_method: str, action_name: str, request_path: str = None):
        """
        :param request_method: 接口请求方法
        :param action_name: 接口名称（后缀）
        :param request_path: 接口请求路径
        """
        self.request_method = request_method.lower()
        self.action_name = action_name
        self.request_path = request_path

        self._params = None
        self._response = None

    def __str__(self):
        return f"<{self.action_name}: {self.request_method}> - {self.request_path}"

    @property
    def params(self):
        return self._params

    @params.setter
    def params(self, params: Dict):
        self._params = params

    @property
    def response(self):
        return self._response

    @response.setter
    def response(self, response: [List, Dict]):
        self._response = response


def assert_handler(action: Action):
    def assert_handler_inner(test_method):
        @wraps(test_method)
        def wrapper(inst, *args, **kwargs):
            try:
                test_method(inst, *args, **kwargs)
            except AssertionError:
                sys.stdout.write(
                    "[×] 「{component}」 {action}\n".format(component=inst.__class__.__name__, action=action)
                )
                raise
            else:
                sys.stdout.write(
                    "[√] 「{component}」 {action}\n".format(component=inst.__class__.__name__, action=action)
                )

        return wrapper

    return assert_handler_inner


class SwaggerViewSetTestMetaClass(type):
    base_action = {
        "list": "get",
        "create": "post",
        "retrieve": "get",
        "update": "put",
        "partial_update": "patch",
        "destroy": "delete",
    }

    def __new__(mcs, name, bases, attrs):
        """
        :param name: 类名称
        :param bases: 类继承的父类集合
        :param attrs: 类的方法集合
        """
        return type.__new__(mcs, name, bases, attrs)

    def __init__(cls, *args, **kwargs):
        if cls.swagger_test_view is None:
            super().__init__(*args, **kwargs)
            return
        action_func_tuples = cls.view_action_func_tuples(cls.swagger_test_view)
        action_list = cls.action_list(cls.swagger_test_view)

        action_name_func_map = {
            cls.func_action(action_func_tuple).action_name: action_func_tuple[ActionFuncIndex.FUNC]
            for action_func_tuple in action_func_tuples
        }

        for action in action_list:
            if action.action_name not in action_name_func_map:
                sys.stdout.write(f"生成测试缺少：{action}\n")
                continue
            if action.action_name in cls.actions_exempt:
                sys.stdout.write(f"skip：{action}\n")
                continue
            cls.fill_mock_data_to_action(action, action_name_func_map[action.action_name])
            setattr(cls, f"test_{action.action_name}_auto", cls.generator_test_func(action))

        super().__init__(*args, **kwargs)

    @classmethod
    def generator_test_func(mcs, action: Action, *args, **kwargs):
        @override_settings(MIDDLEWARE=(OVERRIDE_MIDDLEWARE,))
        @assert_handler(action)
        def test_method(inst):
            response = getattr(inst.client, action.request_method)(
                path=action.request_path.format(**inst.path_params), data=action.params
            )
            try:
                inst.assertExemptDataStructure(response, action.response, value_eq=True)
            except AssertionError:
                sys.stdout.write(f"result: {json.dumps(response, indent=4)}\n")
                sys.stdout.write(f"except: {json.dumps(action.response, indent=4)}\n")
                raise

        return test_method

    @staticmethod
    def action_list(view) -> List[Action]:
        action_list = []
        for endpoint in EndpointEnumerator().get_api_endpoints():
            if endpoint[EndPointIndex.ACTION_FUNC].cls != view:
                continue
            method_lower = endpoint[EndPointIndex.METHOD].lower()
            action_name = endpoint[EndPointIndex.ACTION_FUNC].actions[method_lower]
            action_list.append(
                Action(request_path=endpoint[EndPointIndex.PATH], request_method=method_lower, action_name=action_name)
            )
        return action_list

    @classmethod
    def fill_mock_data_to_action(mcs, action: Action, action_func) -> None:
        try:
            swagger_auto_schema = action_func._swagger_auto_schema
            if action.action_name not in mcs.base_action:
                swagger_auto_schema = swagger_auto_schema[action.request_method]

            if action.request_method in ["get", "delete"]:
                action.params = swagger_auto_schema["query_serializer"].Meta.swagger_schema_fields["example"]
            else:
                action.params = swagger_auto_schema["request_body"].Meta.swagger_schema_fields["example"]

        except Exception:
            action.params = {}

        try:
            swagger_auto_schema = action_func._swagger_auto_schema
            if action.action_name not in mcs.base_action:
                swagger_auto_schema = swagger_auto_schema[action.request_method]
            # TODO 目前只测试成功响应
            action.response = (
                swagger_auto_schema["responses"].get(status.HTTP_200_OK).Meta.swagger_schema_fields["example"]
            )
        except Exception:
            pass

    @classmethod
    def func_action(mcs, action_func_tuple: Tuple) -> Action:
        if action_func_tuple[ActionFuncIndex.FUNC_NAME] in mcs.base_action:
            return Action(
                request_method=mcs.base_action[action_func_tuple[ActionFuncIndex.FUNC_NAME]],
                action_name=action_func_tuple[ActionFuncIndex.FUNC_NAME],
            )
        action_func = action_func_tuple[ActionFuncIndex.FUNC]
        # TODO 暂不考虑一个接口有多种请求方式
        request_method, action_name = list(action_func.mapping.items())[0]
        return Action(request_method=request_method, action_name=action_name)

    @classmethod
    def is_action_func_tuple(mcs, func_tuple: Tuple) -> bool:
        func = func_tuple[ActionFuncIndex.FUNC]
        if func_tuple[ActionFuncIndex.FUNC_NAME] in mcs.base_action or hasattr(func, "url_path"):
            return True
        return False

    @classmethod
    def view_action_func_tuples(mcs, view) -> List[Tuple]:
        return [
            func for func in inspect.getmembers(view, predicate=inspect.isfunction) if mcs.is_action_func_tuple(func)
        ]
