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
from django.utils.translation import ugettext_lazy as _

from apps.exceptions import AppBaseException, ErrorCode


class ConfigTemplateBaseException(AppBaseException):
    MODULE_CODE = ErrorCode.CONFIG_FILE_CODE
    MESSAGE = _("配置模板模块异常")


class ConfigTemplateDoseNotExistException(ConfigTemplateBaseException):
    ERROR_CODE = "001"
    MESSAGE = _("配置模板不存在")


class ConfigVersionDoseNotExistException(ConfigTemplateBaseException):
    ERROR_CODE = "002"
    MESSAGE = _("配置模板版本不存在")


class ConfigTemplateDraftAlreadyExistException(ConfigTemplateBaseException):
    ERROR_CODE = "003"
    MESSAGE = _("配置模板草稿已存在，不允许创建")


class ConfigVersionRenderException(ConfigTemplateBaseException):
    ERROR_CODE = "004"
    MESSAGE = _("模板渲染失败")
    MESSAGE_TPL = _("模板渲染失败，[{error_message}]，请检查模板变量是否正确书写")


class ConfigInstanceDoseNotExistException(ConfigTemplateBaseException):
    ERROR_CODE = "005"
    MESSAGE = _("配置实例不存在")


class ProcessDoseNotBindTemplate(ConfigTemplateBaseException):
    ERROR_CODE = "006"
    MESSAGE = _("进程未绑定配置模板")


class ForbiddenMakoTemplateException(ConfigTemplateBaseException):
    ERROR_CODE = "007"
    MESSAGE = _("Mako模板非法")


class DuplicateTemplateNameException(ConfigTemplateBaseException):
    ERROR_CODE = "008"
    MESSAGE = _("配置模板名称重复")
    MESSAGE_TPL = _("配置模板名称重复[{template_name}]")


class NoActiveConfigVersionException(ConfigTemplateBaseException):
    ERROR_CODE = "009"
    MESSAGE = _("配置模板没有可用的版本")
    MESSAGE_TPL = _("配置模板[{template_name}]没有可用的版本，请对该模板进行保存操作")


class GenerateContextException(ConfigTemplateBaseException):
    ERROR_CODE = "010"
    MESSAGE = _("生成配置Context失败")


class ForbiddenConfigContentException(ConfigTemplateBaseException):
    ERROR_CODE = "011"
    MESSAGE = _("配置文件内容非法")
    MESSAGE_TPL = _("配置文件内容非法, {err_msg}")
