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

from ..base import BaseApi, DataAPI
from ..domains import BSCP_APIGATEWAY_ROOT, BSCP_DIRECT_ROOT


class _BscpApi(BaseApi):
    MODULE = _("蓝鲸配置服务")

    def __init__(self):
        # 传输文件内容，不支持ESB
        self.upload_content = DataAPI(
            method="PUT",
            url=BSCP_DIRECT_ROOT + "/api/v2/file/content/biz/{biz_id}",
            module=self.MODULE,
            description="上传内容",
        )
        self.download_content = DataAPI(
            method="GET",
            url=BSCP_DIRECT_ROOT + "/api/v2/file/content/biz/{biz_id}",
            module=self.MODULE,
            description="下载内容",
        )

        # ESB 接口
        self.create_app = DataAPI(
            method="POST", url=BSCP_APIGATEWAY_ROOT + "create_app/", module=self.MODULE, description="创建应用",
        )
        self.create_config = DataAPI(
            method="POST", url=BSCP_APIGATEWAY_ROOT + "create_config/", module=self.MODULE, description="创建配置",
        )
        self.update_config = DataAPI(
            method="POST", url=BSCP_APIGATEWAY_ROOT + "update_config/", module=self.MODULE, description="更新配置",
        )
        self.delete_config = DataAPI(
            method="POST", url=BSCP_APIGATEWAY_ROOT + "delete_config/", module=self.MODULE, description=u"删除配置",
        )
        self.create_multi_commit = DataAPI(
            method="POST", url=BSCP_APIGATEWAY_ROOT + "create_multi_commit/", module=self.MODULE, description="创建提交",
        )
        self.get_multi_commit = DataAPI(
            method="POST", url=BSCP_APIGATEWAY_ROOT + "get_multi_commit/", module=self.MODULE, description="创建提交",
        )
        self.create_content = DataAPI(
            method="POST", url=BSCP_APIGATEWAY_ROOT + "create_content/", module=self.MODULE, description="创建配置内容",
        )
        self.create_multi_commit_with_content = DataAPI(
            method="POST",
            url=BSCP_APIGATEWAY_ROOT + "create_multi_commit_with_content/",
            module=self.MODULE,
            description=u"附带内容关联, 创建混合提交",
        )
        self.create_procattr = DataAPI(
            method="POST", url=BSCP_APIGATEWAY_ROOT + "create_procattr/", module=self.MODULE, description="创建主机应用归属信息",
        )
        self.create_procattr_batch = DataAPI(
            method="POST",
            url=BSCP_APIGATEWAY_ROOT + "create_procattr_batch/",
            module=self.MODULE,
            description="批量创建主机应用归属信息",
        )
        self.update_procattr = DataAPI(
            method="POST", url=BSCP_APIGATEWAY_ROOT + "update_procattr/", module=self.MODULE, description=u"更新主机应用归属信息",
        )
        self.get_procattr_list_by_app = DataAPI(
            method="POST",
            url=BSCP_APIGATEWAY_ROOT + "get_procattr_list_by_app/",
            module=self.MODULE,
            description="获取主机应用绑定信息",
        )
        self.create_strategy = DataAPI(
            method="POST", url=BSCP_APIGATEWAY_ROOT + "create_strategy/", module=self.MODULE, description="创建策略",
        )
        self.create_multi_release = DataAPI(
            method="POST", url=BSCP_APIGATEWAY_ROOT + "create_multi_release/", module=self.MODULE, description="创建发布",
        )
        self.confirm_multi_commit = DataAPI(
            method="POST", url=BSCP_APIGATEWAY_ROOT + "confirm_multi_commit/", module=self.MODULE, description="确认混合提交"
        )
        self.get_multi_release = DataAPI(
            method="POST", url=BSCP_APIGATEWAY_ROOT + "get_multi_release/", module=self.MODULE, description="查询发布",
        )
        self.publish_multi_release = DataAPI(
            method="POST", url=BSCP_APIGATEWAY_ROOT + "publish_multi_release/", module=self.MODULE, description="发布版本",
        )
        self.get_effected_app_instance_list = DataAPI(
            method="POST",
            url=BSCP_APIGATEWAY_ROOT + "get_effected_app_instance_list/",
            module=self.MODULE,
            description="查询已生效指定版本的应用实例列表",
        )
        self.get_matched_app_instance_list = DataAPI(
            method="POST",
            url=BSCP_APIGATEWAY_ROOT + "get_matched_app_instance_list/",
            module=self.MODULE,
            description="查询指定版本或策略匹配的应用实例列表",
        )
        self.get_app_list = DataAPI(
            method="POST", url=BSCP_APIGATEWAY_ROOT + "get_app_list/", module=self.MODULE, description="获取应用列表",
        )
