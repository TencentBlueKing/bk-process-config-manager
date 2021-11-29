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

# 老版金枪鱼地址
import os
from collections import defaultdict

import requests
from django.db import transaction
from django.utils import timezone
from rest_framework.request import Request

from apps.api import CCApi
from apps.exceptions import AppBaseException
from apps.gsekit.cmdb.constants import BkSetEnv
from apps.gsekit.cmdb.handlers.cmdb import CMDBHandler
from apps.gsekit.configfile.models import ConfigTemplate, ConfigTemplateVersion, ConfigTemplateBindingRelationship
from apps.gsekit.migrate.models import GsekitProcessToCCProcessTemplateMap, MigrationStatus
from apps.gsekit.process.exceptions import DuplicateProcessInstException
from apps.gsekit.process.handlers.process import ProcessHandler
from apps.gsekit.process.models import Process, ProcessInst
from apps.iam import Permission, ResourceEnum
from apps.utils.batch_request import batch_request, request_multi_thread
from apps.utils import basic

DIRECT_OLD_GSEKIT_ROOT = os.getenv("DIRECT_OLD_GSEKIT_ROOT", "http://apps.****.com/ieod-bkapp-gsekit-prod")


class MigrateHandlers(object):
    LEGACY_PROCESS_FIELD_MAP = {
        "StartCmd": {"field": "start_cmd", "description": "启动命令"},
        "StopCmd": {"field": "stop_cmd", "description": "停止命令"},
        "ReloadCmd": {"field": "reload_cmd", "description": "重载命令"},
        "ReStartCmd": {"field": "restart_cmd", "description": "重启命令"},
        "KillCmd": {"field": "face_stop_cmd", "description": "强制停止命令"},
        "OpTimeout": {"field": "timeout", "description": "操作超时时长"},
        "WorkPath": {"field": "work_path", "description": "工作路径"},
        "Seq": {"field": "priority", "description": "启动优先级"},
        "User": {"field": "user", "description": "启动用户"},
        "StartCheckBeginTime": {"field": "bk_start_check_secs", "description": "启动等待时长"},
        "PidFile": {"field": "pid_file", "description": "PID路径"},
        "ProcNum": {"field": "proc_num", "description": "启动数量"},
        "FuncID": {"field": "bk_process_name", "description": "进程别名"},
        "FuncName": {"field": "description", "description": "备注"},
    }

    def __init__(self, bk_biz_id: int, request: Request):
        self.bk_biz_id = int(bk_biz_id)
        self.request = request

    def perform_request(self, uri: str):
        """请求金枪鱼数据，接口不规范，不统一走请求模块，都是get方法，没有参数"""
        response = requests.get(url=f"{DIRECT_OLD_GSEKIT_ROOT}/{uri}/", cookies=self.request.COOKIES)
        return response.json()

    def get_biz_module_bound_processes(self, service_template_id):
        processes = self.perform_request(
            uri=f"api/get_biz_module_bound_processes/{self.bk_biz_id}/{service_template_id}"
        )["objects"]
        return list(filter(lambda process: process["checked"], processes))

    def list_process(self):
        return self.perform_request(uri=f"api/{self.bk_biz_id}/process")["objects"]

    def list_module(self):
        return self.perform_request(uri=f"biz_modules/{self.bk_biz_id}")

    def get_host_no(self, bk_module_id):
        return self.perform_request(uri=f"api/get_host_no/{bk_module_id}")["objects"] or {}

    def get_module_id_host_no_map_list(self, bk_module_id):
        return [{bk_module_id: self.perform_request(uri=f"api/get_host_no/{bk_module_id}")["objects"] or {}}]

    def diff_biz_process(self):
        cmdb_handler = CMDBHandler(bk_biz_id=self.bk_biz_id)

        # 查询GSEKIT模块，并遍历对比差异
        service_template_list = self.list_module()
        for gsekit_service_template in service_template_list:
            gsekit_module_id = gsekit_service_template["ModuleID"]
            gsekit_processes = self.get_biz_module_bound_processes(gsekit_module_id)

            # GSEKIT 在该模块下没有进程，直接跳过
            if not gsekit_processes:
                gsekit_service_template["module_process_difference"] = {
                    "to_be_created_process_templates": [],
                    "to_be_modified_process_templates": [],
                }
                continue

            # 查询CMDB服务模板下的进程，与GSEKIT模块下绑定的进程进行对比
            cmdb_processes = cmdb_handler.process_template(service_template_id=gsekit_module_id)
            gsekit_service_template["module_process_difference"] = self.diff_module_process(
                gsekit_processes, cmdb_processes
            )

        return {
            "runshell_processes": list(filter(lambda proc: proc["Flag"] == "runshell", self.list_process())),
            "service_template_list": service_template_list,
        }

    @MigrationStatus.set_migrate_status(MigrationStatus.MigrateObject.PROCESS)
    def migrate_process(self):
        """迁移进程"""
        diff = self.diff_biz_process()
        for service_template in diff["service_template_list"]:
            module_process_difference = service_template["module_process_difference"]
            to_be_created_process_templates = module_process_difference["to_be_created_process_templates"]
            to_be_modified_process_templates = module_process_difference["to_be_modified_process_templates"]
            if to_be_created_process_templates:
                to_be_created_processes = [
                    {
                        "spec": {
                            "auto_start": {"as_default_value": True, "value": True},
                            "bk_start_check_secs": {
                                "as_default_value": True,
                                "value": int(proc["StartCheckBeginTime"]) or 5,
                            },
                            "bk_func_name": {"as_default_value": True, "value": proc["ProcName"]},
                            "bk_process_name": {"as_default_value": True, "value": proc["FuncID"]},
                            "description": {"as_default_value": True, "value": proc["FuncName"]},
                            "face_stop_cmd": {"as_default_value": True, "value": proc["KillCmd"]},
                            "pid_file": {"as_default_value": True, "value": proc["PidFile"]},
                            "priority": {"as_default_value": True, "value": int(proc["Seq"]) or 1},
                            "proc_num": {"as_default_value": True, "value": int(proc["ProcNum"]) or 1},
                            "reload_cmd": {"as_default_value": True, "value": proc["ReloadCmd"]},
                            "restart_cmd": {"as_default_value": True, "value": proc["ReStartCmd"]},
                            "start_cmd": {"as_default_value": True, "value": proc["StartCmd"]},
                            "stop_cmd": {"as_default_value": True, "value": proc["StopCmd"]},
                            "timeout": {"as_default_value": True, "value": int(proc["OpTimeout"]) or 60},
                            "user": {"as_default_value": True, "value": proc["User"]},
                            "work_path": {"as_default_value": True, "value": proc["WorkPath"]},
                            "bk_start_param_regex": {"as_default_value": True, "value": proc["FuncName"]},
                        }
                    }
                    for proc in to_be_created_process_templates
                ]

                # CMDB限制该接口的processes长度上限为100
                to_be_created_processes_slice_list = basic.list_slice(to_be_created_processes, limit=100)
                params_list = [
                    {
                        "params": {
                            "bk_biz_id": self.bk_biz_id,
                            "service_template_id": int(service_template["ModuleID"]),
                            "processes": to_be_created_processes_slice,
                        }
                    }
                    for to_be_created_processes_slice in to_be_created_processes_slice_list
                ]
                batch_create_results = request_multi_thread(
                    func=CCApi.batch_create_proc_template, params_list=params_list, get_data=lambda x: x
                )
                cmdb_process_templates = CMDBHandler(bk_biz_id=self.bk_biz_id).process_template(
                    process_template_ids=batch_create_results
                )
                to_be_created_map = []
                for gsekit_proc in to_be_created_process_templates:
                    for cmdb_proc in cmdb_process_templates:
                        if (
                            gsekit_proc["ProcName"] == cmdb_proc["property"]["bk_func_name"]["value"]
                            and gsekit_proc["FuncID"] == cmdb_proc["property"]["bk_process_name"]["value"]
                            and gsekit_proc["FuncName"] == cmdb_proc["property"]["bk_start_param_regex"]["value"]
                        ):
                            to_be_created_map.append(
                                GsekitProcessToCCProcessTemplateMap(
                                    bk_biz_id=self.bk_biz_id,
                                    gsekit_process_id=gsekit_proc["ID"],
                                    cc_process_template_id=cmdb_proc["id"],
                                )
                            )
                GsekitProcessToCCProcessTemplateMap.objects.bulk_create(to_be_created_map)

            for proc_tmpl in to_be_modified_process_templates:
                # TODO，修改进程模板
                print(proc_tmpl)

    def diff_module_process(self, gsekit_processes, cmdb_processes):
        # CMDB中，bk_process_name在服务模板下是唯一的
        cmdb_process_map = {cmdb_process["bk_process_name"]: cmdb_process for cmdb_process in cmdb_processes}
        to_be_created_process_templates = []
        to_be_modified_process_templates = []

        for process in gsekit_processes:
            # 忽略runshell的进程，由标准运维迁移为作业平台原子
            if process["Flag"] == "runshell":
                continue

            # 把金枪鱼的FuncID迁移到新版gsekit的bk_process_name
            bk_process_name = process["FuncID"]
            cmdb_process = cmdb_process_map.get(bk_process_name)
            if not cmdb_process:
                # 进程模板在CMDB不存在，则创建
                to_be_created_process_templates.append(process)
                continue

            # 进程模板在CMDB存在，判断进程模板属性是否不一致且需要修改
            modified_fields = []
            for gsekit_field, cmdb_field in self.LEGACY_PROCESS_FIELD_MAP.items():
                source = cmdb_process["property"][cmdb_field["field"]]["value"]
                destination = process[gsekit_field]
                if source != destination:
                    modified_fields.append(
                        {"description": cmdb_field["description"], "source": source, "destination": destination}
                    )
            # 字段都一致，不需要修改
            if modified_fields:
                to_be_modified_process_templates.append(
                    {"bk_process_id": cmdb_process["id"], "modified_fields": modified_fields}
                )
        return {
            "gsekit_processes": gsekit_processes,
            "cmdb_processes": cmdb_processes,
            "to_be_created_process_templates": to_be_created_process_templates,
            "to_be_modified_process_templates": to_be_modified_process_templates,
        }

    def list_config_file(self):
        """金枪鱼 配置文件 列表"""
        return self.perform_request(uri=f"api/{self.bk_biz_id}/{BkSetEnv.FORMAL}/config_file")["objects"]

    def list_config_versions(self, config_template_id):
        return self.perform_request(
            uri=f"api/get_no_draft_versions_by_template_id/{self.bk_biz_id}/{config_template_id}"
        )

    def get_process_templates_with_bound_info(self, bk_process_id):
        """金枪鱼 进程配置文件绑定 列表"""
        templates = self.perform_request(
            uri=f"api/get_process_templates_with_bound_info/{self.bk_biz_id}/{bk_process_id}"
        )["objects"]
        return list(filter(lambda process: process["checked"], templates))

    def migrate_config_file_preview(self):
        """预览需要迁移的配置文件"""
        processes = self.list_process()
        process_templates = []
        for process in processes:
            process_templates.append(
                {"process_info": process, "config_templates": self.get_process_templates_with_bound_info(process["ID"])}
            )

        return {"process_templates": process_templates, "config_templates": self.list_config_file()}

    @MigrationStatus.set_migrate_status(MigrationStatus.MigrateObject.CONFIG)
    def migrate_config_file(self):
        """迁移配置模板"""

        def get_user_group(user: str):
            if user.startswith("user0"):
                return "users"
            else:
                return user

        config_file_preview = self.migrate_config_file_preview()
        to_be_created_config_templates = []
        to_be_created_config_versions = []
        for config_template in config_file_preview["config_templates"]:
            config_template_id = config_template["ConfigTemplateID"]
            created_at = timezone.now()
            created_by = self.request.user.username
            for config_version in self.list_config_versions(config_template_id):
                to_be_created_config_versions.append(
                    ConfigTemplateVersion(
                        config_version_id=config_version["VersionID"],
                        config_template_id=config_template_id,
                        description=f'{config_template["FileName"]} #{config_version["VersionID"]}',
                        content=config_version["FileContent"],
                        is_draft=config_version["Status"] == "formal",
                        is_active=False,
                        file_format="python",
                        created_at=config_version["CreateTime"],
                        created_by=config_version["Creater"],
                        updated_at=config_version["CreateTime"],
                        updated_by=config_version["Creater"],
                    )
                )
                created_at = config_version["CreateTime"]
                created_by = config_version["Creater"]

            filemode = f'0{config_template["FileRight"]}'
            to_be_created_config_templates.append(
                ConfigTemplate(
                    config_template_id=config_template_id,
                    bk_biz_id=self.bk_biz_id,
                    template_name=config_template["TemplateName"],
                    file_name=config_template["FileName"],
                    abs_path=config_template["ConfigPath"],
                    owner=config_template["User"],
                    group=get_user_group(config_template["User"]),
                    filemode=filemode,
                    line_separator=ConfigTemplate.LineSeparator.CRLF
                    if config_template["IsWin"] == "1"
                    else ConfigTemplate.LineSeparator.LF,
                    created_at=created_at,
                    created_by=created_by,
                    updated_at=created_at,
                    updated_by=created_by,
                )
            )

        with transaction.atomic():
            ConfigTemplate.objects.bulk_create(to_be_created_config_templates)
            ConfigTemplateVersion.objects.bulk_create(to_be_created_config_versions)

    @MigrationStatus.set_migrate_status(MigrationStatus.MigrateObject.RELATION)
    def migrate_binding_relation(self):
        """迁移绑定关系"""
        to_be_created_relations = []

        # 查询 金枪鱼进程(1) -> CC3.0进程模板映射表(N)，1对N的关系
        legacy_process_map = defaultdict(list)
        for migrate_process in GsekitProcessToCCProcessTemplateMap.objects.filter(bk_biz_id=self.bk_biz_id):
            legacy_process_map[migrate_process.gsekit_process_id].append(migrate_process.cc_process_template_id)

        for process in self.list_process():
            # 不迁移runshell进程
            if process["Flag"] == "runshell":
                continue

            # 查询在金枪鱼中该进程绑定的配置模板
            checked_templates = self.get_process_templates_with_bound_info(process["ID"])
            for template in checked_templates:

                # 根据进程映射关系，创建gsekit的进程配置绑定关系
                for process_template_id in legacy_process_map[process["ID"]]:
                    to_be_created_relations.append(
                        ConfigTemplateBindingRelationship(
                            bk_biz_id=self.bk_biz_id,
                            config_template_id=template["ConfigTemplateID"],
                            process_object_type=Process.ProcessObjectType.TEMPLATE,
                            process_object_id=process_template_id,
                        )
                    )
        ConfigTemplateBindingRelationship.objects.bulk_create(to_be_created_relations)

    @MigrationStatus.set_migrate_status(MigrationStatus.MigrateObject.PROCESS_INST)
    def migrate_process_instance(self):
        """迁移进程实例，主要是host_num和inst_id"""

        cmdb_handler = CMDBHandler(bk_biz_id=self.bk_biz_id)
        process_handler = ProcessHandler(bk_biz_id=self.bk_biz_id)
        cmdb_handler.get_or_cache_bk_cloud_area(use_cache=False)

        to_be_created_inst = []
        process_list = batch_request(CCApi.list_process_related_info, {"bk_biz_id": self.bk_biz_id})
        migrate_data = process_handler.generate_process_inst_migrate_data(process_list)
        cmdb_module_proc_name_map = migrate_data["cmdb_module_proc_name_map"]
        module_id_host_no_map = {}
        params_list = [{"bk_module_id": bk_module_id} for bk_module_id in cmdb_module_proc_name_map.keys()]
        module_id_host_no_map_list = request_multi_thread(
            self.get_module_id_host_no_map_list, params_list, get_data=lambda x: x
        )
        for _module_id_host_no_map in module_id_host_no_map_list:
            module_id_host_no_map.update(_module_id_host_no_map)
        for bk_module_id, cmdb_process_name_map in cmdb_module_proc_name_map.items():
            host_no_map = module_id_host_no_map[bk_module_id]
            for process_name, processes in cmdb_process_name_map.items():
                max_proc_num = processes["max_proc_num"]

                for cmdb_process in processes["processes"]:
                    bk_host_innerip = cmdb_process["host"]["bk_host_innerip"]
                    bk_cloud_id = cmdb_process["host"]["bk_cloud_id"]
                    bk_host_num = host_no_map.get(bk_host_innerip)
                    # 金枪鱼中没有主机编号，直接跳过
                    if not bk_host_num:
                        continue

                    cmdb_proc_num = cmdb_process["process"]["proc_num"]
                    bk_host_num = int(bk_host_num)
                    for local_inst_id in range(1, cmdb_proc_num + 1):
                        inst_id = (bk_host_num - 1) * max_proc_num + local_inst_id
                        local_inst_id_key = ProcessInst.LOCAL_INST_ID_UNIQ_KEY_TMPL.format(
                            bk_host_innerip=bk_host_innerip,
                            bk_cloud_id=bk_cloud_id,
                            bk_process_name=process_name,
                            local_inst_id=local_inst_id,
                        )
                        to_be_created_inst.append(
                            ProcessInst(
                                bk_biz_id=self.bk_biz_id,
                                bk_host_num=bk_host_num,
                                bk_module_id=bk_module_id,
                                bk_host_innerip=bk_host_innerip,
                                bk_cloud_id=bk_cloud_id,
                                bk_process_id=cmdb_process["process"]["bk_process_id"],
                                bk_process_name=process_name,
                                inst_id=inst_id,
                                local_inst_id=local_inst_id,
                                local_inst_id_uniq_key=local_inst_id_key,
                                proc_num=cmdb_proc_num,
                            )
                        )
        # 检查待创建实例中不符合唯一键的项
        uniq_key_set = set()
        duplicate_proc_instances = set()
        for inst in to_be_created_inst:
            if inst.local_inst_id_uniq_key in uniq_key_set:
                duplicate_proc_instances.add(inst.local_inst_id_uniq_key)
                continue
            uniq_key_set.add(inst.local_inst_id_uniq_key)

        # 存在重复进程实例
        if duplicate_proc_instances:
            raise DuplicateProcessInstException(uniq_key=duplicate_proc_instances)

        with transaction.atomic():
            # 删除已同步的进程实例，使用金枪鱼的数据进行重建后再执行同步
            ProcessInst.objects.filter(bk_biz_id=self.bk_biz_id).delete()
            ProcessInst.objects.bulk_create(to_be_created_inst)

    @MigrationStatus.set_migrate_status(MigrationStatus.MigrateObject.IAM)
    def migrate_iam(self, perm_gainer=None):
        """迁移权限，仅迁移配置管理权限，其它权限由权限中心统一处理"""
        for config_template in ConfigTemplate.objects.filter(bk_biz_id=self.bk_biz_id):
            attribute = {
                "id": str(config_template.config_template_id),
                "name": config_template.template_name,
                "bk_biz_id": self.bk_biz_id,
            }
            resource = ResourceEnum.CONFIG_TEMPLATE.create_instance(str(config_template.config_template_id), attribute)
            # 新建授权
            result, msg = Permission().grant_creator_action(
                resource=resource,
                creator=perm_gainer or config_template.created_by,
            )
            if not result:
                raise AppBaseException(msg)
