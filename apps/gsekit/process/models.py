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
from collections import defaultdict
from typing import Dict, List

from django.db import models
from django.utils.translation import ugettext_lazy as _

from apps.gsekit.cmdb.constants import BK_SET_ENV_CHOICES
from apps.gsekit.process.exceptions import ProcessInstDoseNotExistException, GenerateProcessObjException


class Process(models.Model):
    class ProcessObjectType(object):
        INSTANCE = "INSTANCE"
        TEMPLATE = "TEMPLATE"

    PROCESS_OBJECT_TYPE_CHOICE = (
        (ProcessObjectType.INSTANCE, _("进程实例")),
        (ProcessObjectType.TEMPLATE, _("进程模板")),
    )

    class ProcessStatus(object):
        # 对于GSE，0/2都为终止状态
        UNREGISTERED = 0
        RUNNING = 1
        TERMINATED = 2

    PROCESS_STATUS_CHOICE = (
        (ProcessStatus.RUNNING, _("运行中")),
        (ProcessStatus.TERMINATED, _("未运行")),
    )

    IS_AUTO_CHOICE = ((False, _("未托管")), (True, _("已托管")))

    bk_biz_id = models.IntegerField(_("业务ID"), db_index=True)
    expression = models.CharField(_("实例表达式"), max_length=256, db_index=True, default=_("待完善"))
    bk_host_innerip = models.GenericIPAddressField(_("主机IP"), db_index=True)
    bk_cloud_id = models.IntegerField(_("云区域ID"), db_index=True)
    bk_set_env = models.CharField(_("集群环境类型"), choices=BK_SET_ENV_CHOICES, max_length=4, db_index=True)
    bk_set_id = models.IntegerField(_("集群ID"), db_index=True)
    bk_module_id = models.IntegerField(_("模块ID"), db_index=True)
    service_template_id = models.IntegerField(_("服务模板ID"), null=True, blank=True, db_index=True)
    service_instance_id = models.IntegerField(_("服务实例ID"), db_index=True)
    bk_process_name = models.CharField(_("进程名称"), max_length=64, null=True, blank=True, db_index=True)
    bk_process_id = models.IntegerField(_("进程ID"), primary_key=True)
    process_template_id = models.IntegerField(_("进程模板ID"), db_index=True)
    process_status = models.IntegerField(_("进程状态"), db_index=True, default=ProcessStatus.TERMINATED)
    is_auto = models.BooleanField(_("托管状态"), db_index=True, default=False)

    @classmethod
    def generate_process_obj(cls, bk_process_id: int = None, process_template_id: int = None) -> Dict:
        # 优先判定为进程模板
        if process_template_id:
            return {"process_object_type": cls.ProcessObjectType.TEMPLATE, "process_object_id": process_template_id}
        elif bk_process_id:
            return {"process_object_type": cls.ProcessObjectType.INSTANCE, "process_object_id": bk_process_id}
        else:
            raise GenerateProcessObjException()

    def to_process_obj(self) -> Dict:
        return self.generate_process_obj(bk_process_id=self.bk_process_id, process_template_id=self.process_template_id)

    class Meta:
        verbose_name = _("业务进程（Process）")
        verbose_name_plural = _("业务进程（Process）")


class ProcessInst(models.Model):
    # 默认启动数量
    DEFAULT_PROC_NUM = 1
    LOCAL_INST_ID_UNIQ_KEY_TMPL = "{bk_host_innerip}-{bk_cloud_id}-{bk_process_name}-{local_inst_id}"
    INST_ID_UNIQ_KEY_TMPL = "{bk_module_id}-{bk_process_name}-{inst_id}"
    BK_HOST_NUM_KEY_TMPL = "{bk_host_innerip}-{bk_cloud_id}-{bk_process_name}"

    bk_biz_id = models.IntegerField(_("业务ID"), db_index=True)
    bk_host_num = models.IntegerField(_("主机编号"), db_index=True)
    bk_host_innerip = models.GenericIPAddressField(_("主机IP"), db_index=True)
    bk_cloud_id = models.IntegerField(_("云区域ID"), db_index=True)
    bk_process_id = models.IntegerField(_("进程ID"), db_index=True)
    bk_module_id = models.IntegerField(_("模块ID"), db_index=True)
    bk_process_name = models.CharField(_("进程名称"), max_length=64, db_index=True)
    inst_id = models.IntegerField(_("InstID"), db_index=True)
    process_status = models.IntegerField(_("进程状态"), db_index=True, default=Process.ProcessStatus.TERMINATED)
    is_auto = models.BooleanField(_("托管状态"), db_index=True, default=False)
    local_inst_id = models.IntegerField(_("LocalInstID"), db_index=True)
    local_inst_id_uniq_key = models.CharField(_("进程实例唯一标识"), max_length=256, db_index=True, default="")
    proc_num = models.IntegerField(_("启动数量"), default=DEFAULT_PROC_NUM)

    @classmethod
    def get_process_inst_map(cls, bk_process_ids: List[int]) -> Dict:
        """根据进程ID列表查询"""
        proc_inst_map = defaultdict(list)
        for proc_inst in ProcessInst.objects.filter(bk_process_id__in=bk_process_ids).values(
            "bk_process_id", "inst_id", "local_inst_id"
        ):
            proc_inst_map[proc_inst["bk_process_id"]].append(
                {"inst_id": proc_inst["inst_id"], "local_inst_id": proc_inst["local_inst_id"]}
            )
        return proc_inst_map

    @classmethod
    def get_single_inst(cls, bk_process_id):
        """根据bk_process_id获取第一个实例"""
        proc_inst = cls.objects.filter(bk_process_id=bk_process_id).first()
        if not proc_inst:
            raise ProcessInstDoseNotExistException()
        return proc_inst

    @property
    def inst_id_uniq_key(self):
        return self.INST_ID_UNIQ_KEY_TMPL.format(
            bk_module_id=self.bk_module_id, bk_process_name=self.bk_process_name, inst_id=self.inst_id
        )

    @property
    def bk_host_num_key(self):
        return self.BK_HOST_NUM_KEY_TMPL.format(
            bk_host_innerip=self.bk_host_innerip, bk_cloud_id=self.bk_cloud_id, bk_process_name=self.bk_process_name
        )

    class Meta:
        unique_together = [
            ["bk_module_id", "bk_process_name", "inst_id"],
            ["bk_host_innerip", "bk_cloud_id", "bk_process_name", "local_inst_id"],
        ]
        verbose_name = _("进程实例（ProcessInst）")
        verbose_name_plural = _("进程实例（ProcessInst）")
