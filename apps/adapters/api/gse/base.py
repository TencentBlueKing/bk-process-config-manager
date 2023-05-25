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
import abc
import typing
from apps.api import GseApi

InfoDict = typing.Dict[str, typing.Any]
InfoDictList = typing.List[InfoDict]
AgentIdInfoMap = typing.Dict[str, InfoDict]


class GseApiBaseHelper(abc.ABC):

    version: str = None
    gse_api_obj = None

    def __init__(self, version: str, gse_api_obj=GseApi):
        self.version = version
        self.gse_api_obj = gse_api_obj

    @abc.abstractmethod
    def get_agent_id(self, mixed_types_of_host_info: typing.Union[InfoDict, typing.Dict]) -> str:
        """
        获取 Agent 唯一标识
        :param mixed_types_of_host_info: 携带主机信息的混合类型对象
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def preprocessing_proc_operate_info(self, host_info_list: InfoDictList, proc_operate_info: InfoDict) -> InfoDict:
        """
        进程操作信息预处理
        :param host_info_list: 主机信息列表
        :param proc_operate_info: 进程操作信息
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def _operate_proc_multi(self, proc_operate_req: InfoDictList, **options) -> str:
        """
        批量进程操作
        :param proc_operate_req: 进程操作信息列表
        :param options: 其他可能需要的参数
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_proc_operate_result(self, task_id: str) -> InfoDict:
        """
        获取进程操作结果
        :param task_id: GSE 任务 ID
        :return:
        """
        raise NotImplementedError

    def operate_proc_multi(self, proc_operate_req: InfoDictList, **options) -> str:
        """
        批量进程操作
        :param proc_operate_req: 进程操作信息列表
        :param options: 其他可能需要的参数
        :return:
        """
        preprocessed_proc_operate_req: InfoDictList = []
        for proc_operate_info in proc_operate_req:
            hosts = proc_operate_info.pop("hosts")
            preprocessed_proc_operate_req.append(self.preprocessing_proc_operate_info(hosts, proc_operate_info))
        return self._operate_proc_multi(preprocessed_proc_operate_req, **options)

    def get_gse_proc_key(
        self, mixed_types_of_host_info: typing.Union[InfoDict, typing.Dict], namespace: str, proc_name: str, **options
    ) -> str:
        """
        获取进程唯一标识
        :param mixed_types_of_host_info: 携带主机信息的混合类型对象
        :param namespace: 命名空间
        :param proc_name: 进程名称
        :param options: 其他可能需要的关键字参数
        :return:
        """
        return f"{self.get_agent_id(mixed_types_of_host_info)}:{namespace}:{proc_name}"
