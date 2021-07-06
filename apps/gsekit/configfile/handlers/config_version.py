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
import re
from typing import Dict

from django.core.cache import cache
from django.utils.translation import ugettext as _
from lxml import etree

from apps.gsekit.cmdb.handlers.cmdb import CMDBHandler
from apps.gsekit.configfile import exceptions
from apps.gsekit.configfile.exceptions import (
    ConfigTemplateDoseNotExistException,
    GenerateContextException,
    NoActiveConfigVersionException,
)
from apps.gsekit.configfile.models import ConfigTemplate, ConfigTemplateVersion
from apps.gsekit.process.models import ProcessInst
from apps.utils import APIModel
from apps.utils.mako_utils.context import MakoSandbox
from apps.utils.mako_utils.render import mako_render
from apps.utils.models import model_to_dict
from common.log import logger

RE_INCLUDE = re.compile(r"""^#\s*Ginclude\s+["'](?P<template_name>[^"']*)["']\s*$""", re.M)

HELP_TEMPLATE = """
<%
import datetime
%>
***********************************
* NOW: ${datetime.datetime.now()} *
***********************************

********************
* Global Variables *
********************

% for k, v in global_variables.items():
    % if k == "global_variables":
        <% continue %>
    % endif
<%text>${</%text> ${k} <%text>}</%text> = ${v}
% endfor

*****************
* 'this' object *
*****************

===========
this.attrib
===========

% if len(this.attrib):
    % for k, v in this.attrib.items():
<%text>${</%text> this.attrib["${k}"] <%text>}</%text> = ${v}
    % endfor
% else:
<empty>
% endif

===========
this.cc_set
===========

% for k, v in this.cc_set.attrib.items():
<%text>${</%text> this.cc_set.attrib["${k}"] <%text>}</%text> = ${v}
% endfor

==============
this.cc_module
==============

% for k, v in this.cc_module.attrib.items():
<%text>${</%text> this.cc_module.attrib["${k}"] <%text>}</%text> = ${v}
% endfor

============
this.cc_host
============

% for k, v in this.cc_host.attrib.items():
<%text>${</%text> this.cc_host.attrib["${k}"] <%text>}</%text> = ${v}
% endfor


***************
* 'cc' object *
***************

=====================
find all host element
=====================

<%text>
% for host in cc.findall('.//Host'):
    ${host.attrib['InnerIP'] }
% endfor
</%text>

% for host in cc.findall('.//Host'):
    ${host.attrib['InnerIP'] }
% endfor

==========================================
find all host element of module "gamesvr"
==========================================

<%text>
% for host in cc.findall('.//Module[@ModuleName="gamesvr"]/Host'):
    ${host.attrib['InnerIP'] }
% endfor
</%text>
% for host in cc.findall('.//Module[@ModuleName="gamesvr"]/Host'):
    ${host.attrib['InnerIP'] }
% endfor

==================================
find all host element of set "qq"
==================================

<%text>
% for host in cc.findall('.//Set[@SetName="qq"]//Host'):
    ${host.attrib['InnerIP'] }
% endfor
</%text>

% for host in cc.findall('.//Set[@SetName="qq"]//Host'):
    ${host.attrib['InnerIP'] }
% endfor

************
* end help *
************
"""

TEMPLATE_CACHE = {}


class ReadOnlyDict(dict):
    """
    A read-only dict class for GseKit
    """

    def __readonly__(self, key, *args, **kwargs):
        raise RuntimeError("`this.attrib['%s']` is read only" % key)

    __setitem__ = __readonly__
    __delitem__ = __readonly__

    del __readonly__


class ContextDict(object):
    """
    Custom dict-like class for GseKit
    """

    def __init__(self, attrib):
        self.attrib = attrib

    @staticmethod
    def __usage__(key, *args, **kwargs):
        message = "use `this.attrib['%s']` instead of `this['%s']`" % (key, key)
        raise RuntimeError(message)

    __getitem__ = __usage__
    __setitem__ = __usage__

    del __usage__


class ConfigVersionHandler(APIModel):
    def __init__(self, config_version_id: int = None, config_version_obj: ConfigTemplateVersion = None):
        super().__init__()
        self.config_version_id = int(config_version_id)
        self.config_version = config_version_obj

    def _get_data(self) -> ConfigTemplateVersion:
        if self.config_version:
            return self.config_version
        try:
            config_version = ConfigTemplateVersion.objects.get(config_version_id=self.config_version_id)
        except ConfigTemplateVersion.DoesNotExist:
            logger.error("配置模板版本不存在, config_version_id={}".format(self.config_version_id))
            raise exceptions.ConfigVersionDoseNotExistException()
        return config_version

    @property
    def data(self) -> ConfigTemplateVersion:
        return super().data

    def update(self, description: str, content: str, is_draft: bool, is_active: bool, file_format: str = None) -> Dict:
        self.data.description = description
        self.data.content = content
        # 将草稿置为可用时，把其它版本都置为不可用
        if self.data.is_draft is True and is_draft is False and is_active is True:
            ConfigTemplateVersion.objects.filter(config_template_id=self.data.config_template_id).update(
                is_active=False, skip_update_time=True, skip_update_user=True
            )
        self.data.is_draft = is_draft
        self.data.is_active = is_active
        if file_format:
            self.data.file_format = file_format
        self.data.save()
        return model_to_dict(self.data)

    def clone(self, description: str) -> Dict:
        """
        从已有的配置版本中克隆一份
        :param description: 配置模板版本描述
        :return:
        """
        try:
            # 若存在草稿，则直接覆盖草稿
            config_version = ConfigTemplateVersion.objects.get(
                config_template_id=self.data.config_template_id, is_draft=True
            )
        except ConfigTemplateVersion.DoesNotExist:
            # 若不存在草稿，则新建
            config_version = ConfigTemplateVersion(config_template_id=self.data.config_template_id)
        config_version.description = description
        config_version.content = self.data.content
        config_version.is_draft = True
        config_version.is_active = False
        config_version.save()
        return model_to_dict(config_version)

    @classmethod
    def fill_template_dependencies(cls, bk_biz_id, content: str):
        """递归填充模板依赖"""
        for matched_text in RE_INCLUDE.finditer(content):
            dependence_template_name = matched_text.groupdict()["template_name"]
            include_line = matched_text.group()
            try:
                dependence_config_template = ConfigTemplate.objects.get(
                    bk_biz_id=bk_biz_id, template_name=dependence_template_name
                )
                config_template_id = dependence_config_template.config_template_id
                latest_config_version = ConfigTemplateVersion.get_latest_version_mapping([config_template_id]).get(
                    config_template_id
                )
                if latest_config_version is None:
                    raise NoActiveConfigVersionException(template_name=dependence_template_name)
                content = content.replace(include_line, latest_config_version.content)
            except ConfigTemplate.DoesNotExist:
                raise ConfigTemplateDoseNotExistException(
                    "依赖模板[{template_name}]不存在，请注意Ginclude的是模板名称，不是文件名称".format(template_name=dependence_template_name)
                )
            except ConfigTemplate.MultipleObjectsReturned:
                raise ConfigTemplateDoseNotExistException(
                    "依赖模板[{template_name}]不唯一，请重命名依赖".format(template_name=dependence_template_name)
                )
            else:
                # 递归继续寻找依赖
                return cls.fill_template_dependencies(bk_biz_id, content)
        return content

    @classmethod
    def get_process_context(
        cls,
        process_info: Dict,
        bk_biz_id: int,
        inst_id: int,
        local_inst_id: int,
        cc_context=None,
        biz_global_variables=None,
        xpath_cache=None,
        with_help=False,
    ) -> Dict:
        bk_process_id = process_info["process"]["bk_process_id"]
        bk_process_name = process_info["process"]["bk_process_name"]
        bk_set_name = process_info["set"]["bk_set_name"]
        bk_module_name = process_info["module"]["bk_module_name"]
        bk_host_innerip = process_info["host"]["bk_host_innerip"]
        bk_cloud_id = process_info["host"]["bk_cloud_id"]
        bk_set_env = process_info["set"]["bk_set_env"]

        if cc_context is None:
            cc_context = cls.get_cc_context(bk_biz_id, bk_set_env)
        if biz_global_variables is None:
            biz_global_variables = CMDBHandler(bk_biz_id=bk_biz_id).biz_global_variables()
        if xpath_cache is None:
            xpath_cache = {}

        attrib = {}
        this_context = ContextDict(ReadOnlyDict(attrib))

        cc_set_path = f'Set[@SetName="{bk_set_name}"]'
        if xpath_cache.get(cc_set_path) is not None:
            cc_set_context = xpath_cache.get(cc_set_path)
        else:
            cc_set_context = cc_context.find(cc_set_path)
            xpath_cache[cc_set_path] = cc_set_context
        setattr(this_context, "cc_set", cc_set_context)

        cc_module_path = f'Set[@SetName="{bk_set_name}"]/Module[@ModuleName="{bk_module_name}"]'
        if xpath_cache.get(cc_module_path) is not None:
            cc_module_context = xpath_cache.get(cc_module_path)
        else:
            cc_module_context = cc_context.find(cc_module_path)
            xpath_cache[cc_module_path] = cc_module_context
        setattr(this_context, "cc_module", cc_module_context)

        cc_host_path = (
            f'Set[@SetName="{bk_set_name}"]/'
            f'Module[@ModuleName="{bk_module_name}"]/'
            f'Host[lcontains(tokenize(@InnerIP, ","), "{bk_host_innerip}") and @bk_cloud_id="{bk_cloud_id}"]'
        )
        if xpath_cache.get(cc_host_path) is not None:
            cc_host_context = xpath_cache.get(cc_host_path)
        else:
            cc_host_context = cc_context.xpath(cc_host_path)[0]
            xpath_cache[cc_host_path] = cc_host_context
        try:
            setattr(this_context, "cc_host", cc_host_context)
        except IndexError:
            raise GenerateContextException(_("context[cc_host]生成失败"))

        context = {
            "Scope": f"{bk_set_name}.{bk_module_name}.{process_info['service_instance']['name']}"
            f".{bk_process_name}.{bk_process_id}",
            "FuncID": bk_process_name,
            "InstID": inst_id,
            "InstID0": inst_id - 1,
            "LocalInstID": local_inst_id,
            "LocalInstID0": local_inst_id - 1,
            "bk_set_name": bk_set_name,
            "bk_module_name": bk_module_name,
            "bk_host_innerip": bk_host_innerip,
            "bk_cloud_id": bk_cloud_id,
            "bk_process_id": bk_process_id,
            "bk_process_name": bk_process_name,
            "FuncName": process_info["process"]["bk_func_name"],
            "ProcName": process_info["process"]["bk_process_name"],
            "WorkPath": process_info["process"]["work_path"],
            "PidFile": process_info["process"]["pid_file"],
            "this": this_context,
            "cc": cc_context,
        }

        # 补充内置字段
        for bk_obj_id, bk_obj_variables in biz_global_variables.items():
            for variable in bk_obj_variables:
                if bk_obj_id == CMDBHandler.BK_GLOBAL_OBJ_ID:
                    continue
                bk_property_id = variable["bk_property_id"]
                context[bk_property_id] = getattr(this_context, f"cc_{bk_obj_id}").attrib.get(bk_property_id)

        context["global_variables"] = context
        if with_help:
            with MakoSandbox():
                context["HELP"] = mako_render(HELP_TEMPLATE, context)
        return context

    @classmethod
    def get_cc_context(cls, bk_biz_id: int, bk_set_env: str):

        cc_xml_doc = cache.get(CMDBHandler.CACHE_TOPO_ATTR_TEMPLATE.format(bk_biz_id=bk_biz_id))
        if cc_xml_doc is None:
            cc_xml_doc = CMDBHandler(bk_biz_id=bk_biz_id).cache_topo_tree_attr(bk_set_env)
        try:
            cc_context = etree.fromstring(cc_xml_doc)
        except ValueError as err:
            logger.exception(f"{err}, etree.fromstring error, cc_xml_doc: {cc_xml_doc}")
            raise err
        return cc_context

    @classmethod
    def render(cls, bk_biz_id: int, process_info: dict, content: str):
        """
        渲染
        :param bk_biz_id: 业务ID
        :param content: 模板内容
        :param process_info: 进程实例
        :return:
        """
        bk_process_id = process_info["process"]["bk_process_id"]
        proc_inst = ProcessInst.get_single_inst(bk_process_id=bk_process_id)
        content = cls.fill_template_dependencies(bk_biz_id, content)
        context = cls.get_process_context(
            process_info=process_info,
            bk_biz_id=bk_biz_id,
            inst_id=proc_inst.inst_id,
            local_inst_id=proc_inst.local_inst_id,
            with_help="${HELP}" in content,
        )
        return mako_render(content, context)
