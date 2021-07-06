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
import io
import logging
from collections import defaultdict
from typing import Dict

from django.core.cache import cache

from apps.api import BscpApi
from apps.exceptions import ApiResultError
from apps.gsekit.adapters import BscpAdapter
from apps.gsekit.adapters.bscp.constants import (
    MAX_PAGE_LIMIT,
    RELEASE_TIMEOUT_SEC,
    EffectCode,
)
from apps.gsekit.adapters.bscp.exceptions import BscpErrorCode, ReleaseConfigException
from apps.gsekit.adapters.bscp.models import BscpConfig
from apps.gsekit.configfile.exceptions import ProcessDoseNotBindTemplate
from apps.gsekit.configfile.models import ConfigInstance, ConfigTemplate
from apps.gsekit.constants import CacheExpire
from apps.gsekit.job.models import JobStatus, JobTask
from apps.gsekit.pipeline_plugins.components.collections.base import (
    POLLING_INTERVAL,
    JobTaskBaseService,
    MultiJobTaskBaseService,
)
from apps.gsekit.process.models import Process
from apps.utils.batch_request import batch_request, request_multi_thread
from pipeline.component_framework.component import Component
from pipeline.core.flow import StaticIntervalGenerator

logger = logging.getLogger("celery")

bscp_adapter = BscpAdapter()


class UploadContentService(JobTaskBaseService):
    """
    上传文件内容 -> BSCP -> 制品库
    """

    def _execute(self, data, parent_data):
        job_task = data.get_one_of_inputs("job_task")

        inst_id = job_task.extra_data["inst_id"]

        process_info = job_task.extra_data["process_info"]
        process_obj = Process.generate_process_obj(
            bk_process_id=process_info["process"]["bk_process_id"],
            process_template_id=process_info["process_template"].get("id") or 0,
        )
        bscp_app = bscp_adapter.get_or_create_app(
            process_info["process"]["bk_biz_id"], process_obj["process_object_type"], process_obj["process_object_id"]
        )
        bscp_base_params = {"biz_id": bscp_app.biz_id, "app_id": bscp_app.app_id}
        config_template_ids = job_task.get_job_task_config_template_ids()
        if not config_template_ids:
            raise ProcessDoseNotBindTemplate()

        # 对每个文件内容提交到制品库
        for config_instance in ConfigInstance.objects.filter(
            config_template_id__in=config_template_ids,
            bk_process_id=job_task.bk_process_id,
            is_latest=True,
            inst_id=inst_id,
        ):
            logger.info(f"[UploadContentService] uploading config instance [{config_instance.id}] to bscp")
            BscpApi.upload_content(
                params={"biz_id": bscp_app.biz_id, "file": io.BytesIO(config_instance.content)},
                headers={"X-Bkapi-File-Content-Id": config_instance.sha256, "X-Bkapi-File-Content-Overwrite": "true"},
            )

            bk_host_innerip = job_task.extra_data["process_info"]["host"]["bk_host_innerip"]
            cloud_id = str(job_task.extra_data["process_info"]["host"]["bk_cloud_id"])

            cache_key = (
                f"procattr-{bscp_app.biz_id}-{bscp_app.app_id}" f"-{bk_host_innerip}-{cloud_id}-{config_instance.path}"
            )
            if cache.get(cache_key):
                # 已设置 procattr
                continue

            procattr = dict(
                ip=bk_host_innerip,
                cloud_id=cloud_id,
                path="/",
                labels={"ip": bk_host_innerip, "cloud_id": cloud_id},
                **bscp_base_params,
            )

            logger.info(f"[UploadContentService] create_procattr for config instance [{config_instance.id}]")
            try:
                BscpApi.create_procattr(procattr)
            except ApiResultError as error:
                if error.code == BscpErrorCode.PROC_ATTR_ALREADY_EXIST:
                    BscpApi.update_procattr(procattr)
                else:
                    raise error
            cache.set(cache_key, True, CacheExpire.HOUR)
        return self.return_data(result=True)

    def inputs_format(self):
        return super().inputs_format() + [
            JobTaskBaseService.InputItem(name="bk_biz_id", key="bk_biz_id", required=True)
        ]


class CommitAndReleaseService(MultiJobTaskBaseService):
    __need_schedule__ = True
    interval = StaticIntervalGenerator(POLLING_INTERVAL)

    def _execute(self, data, parent_data) -> Dict:
        job_task = data.get_one_of_inputs("job_task")
        job_task_ids = data.get_one_of_inputs("job_task_ids")
        config_template_ids = job_task.get_job_task_config_template_ids()
        if not config_template_ids:
            # 未绑定模板，忽略
            for job_task in JobTask.objects.filter(id__in=job_task_ids):
                job_task.set_status(
                    JobStatus.IGNORED, extra_data={"failed_reason": str(ProcessDoseNotBindTemplate().message)}
                )
            self.finish_schedule()
            return self.return_data(result=True)

        process_info = job_task.extra_data["process_info"]
        process_obj = Process.generate_process_obj(
            bk_process_id=process_info["process"]["bk_process_id"],
            process_template_id=process_info["process_template"].get("id") or 0,
        )
        bscp_app = bscp_adapter.get_or_create_app(
            process_info["process"]["bk_biz_id"], process_obj["process_object_type"], process_obj["process_object_id"]
        )
        bscp_base_params = {"biz_id": bscp_app.biz_id, "app_id": bscp_app.app_id}

        # 查询BSCP配置，若不存在则新建
        bscp_configs = list(
            BscpConfig.objects.filter(config_template_id__in=config_template_ids, app_id=bscp_app.app_id)
        )
        to_be_created_bscp_configs = {}
        bscp_config_tmpl_id_name_path_map = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
        """
        bscp_config_tmpl_id_name_path_map 数据格式如下
        bscp_config_tmpl_id_name_path_map = {
            1: {
                "path": {
                    "file_name": bscp_config
                }
            }
        }
        """
        for bscp_config in bscp_configs:
            bscp_config_tmpl_id_name_path_map[bscp_config.config_template_id][bscp_config.path][
                bscp_config.file_name
            ] = bscp_config

        bk_process_ids = set()
        process_inst_map = {}
        process_inst_map_key_tmpl = "{bk_process_id}-{inst_id}"
        for job_task in JobTask.objects.filter(id__in=job_task_ids):
            bk_process_id = job_task.extra_data["process_info"]["process"]["bk_process_id"]
            inst_id = job_task.extra_data["inst_id"]
            bk_process_ids.add(bk_process_id)
            process_inst_map[process_inst_map_key_tmpl.format(bk_process_id=bk_process_id, inst_id=inst_id)] = job_task

        config_template_id_obj_map = {
            config_template.config_template_id: config_template
            for config_template in ConfigTemplate.objects.filter(config_template_id__in=config_template_ids)
        }
        config_tmpl_inst_map = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
        strategy_labels = []
        for config_instance in ConfigInstance.objects.filter(
            config_template_id__in=config_template_ids, bk_process_id__in=bk_process_ids, is_latest=True
        ):
            inst_job_task = process_inst_map.get(
                process_inst_map_key_tmpl.format(
                    bk_process_id=config_instance.bk_process_id, inst_id=config_instance.inst_id
                )
            )

            if not inst_job_task:
                continue

            # 更新config_instances
            config_instances = inst_job_task.extra_data["config_instances"]
            config_instance_ids = {config_instance["id"] for config_instance in config_instances}
            if config_instance.id not in config_instance_ids:
                config_instances.append(
                    {
                        "id": config_instance.id,
                        "config_template_id": config_instance.config_template_id,
                        "template_name": config_template_id_obj_map[config_instance.config_template_id].template_name,
                        "file_name": config_template_id_obj_map[config_instance.config_template_id].file_name,
                        "inst_id": config_instance.inst_id,
                        "path": config_instance.path,
                    }
                )
            inst_job_task.extra_data["config_instances"] = config_instances
            inst_job_task.save(update_fields=["extra_data"])

            host_info = inst_job_task.extra_data["process_info"]["host"]
            labels = {
                "labels": {
                    "cloud_id": "eq|{bk_cloud_id}".format(bk_cloud_id=host_info["bk_cloud_id"]),
                    "ip": "eq|{bk_host_innerip}".format(bk_host_innerip=host_info["bk_host_innerip"]),
                }
            }
            strategy_labels.append(labels)

            if not bscp_config_tmpl_id_name_path_map[config_instance.config_template_id][config_instance.path][
                config_instance.name
            ]:
                # 此时代表bscp config 未创建，需进行创建
                to_be_created_bscp_configs[
                    f"{config_instance.config_template_id}-{config_instance.path}-{config_instance.name}"
                ] = {
                    "config_template": config_template_id_obj_map[config_instance.config_template_id],
                    "file_name": config_instance.name,
                    "path": config_instance.path,
                    "bscp_app": bscp_app,
                }
            config_tmpl_inst_map[config_instance.config_template_id][config_instance.path][config_instance.name].append(
                {"content_id": config_instance.sha256, "labels_and": [labels]},
            )

        for to_be_created_bscp_config in to_be_created_bscp_configs.values():
            bscp_config = bscp_adapter.get_or_create_config(**to_be_created_bscp_config)
            bscp_configs.append(bscp_config)

        # 创建批量提交ID
        multi_commit_id = BscpApi.create_multi_commit_with_content(
            dict(
                memo="gsekit commit",
                metadatas=[
                    {
                        "cfg_id": bscp_config.cfg_id,
                        "contents": config_tmpl_inst_map[bscp_config.config_template_id][bscp_config.path][
                            bscp_config.file_name
                        ],
                    }
                    for bscp_config in bscp_configs
                    if config_tmpl_inst_map[bscp_config.config_template_id][bscp_config.path][bscp_config.file_name]
                ],
                **bscp_base_params,
            )
        )["multi_commit_id"]

        # 确认提交
        BscpApi.confirm_multi_commit(dict(multi_commit_id=multi_commit_id, **bscp_base_params))

        # 创建策略
        try:
            strategy_id = BscpApi.create_strategy(
                dict(name=f"gsekit_strategy_{job_task.id}", labels_and=strategy_labels, **bscp_base_params,)
            )["strategy_id"]
        except ApiResultError as error:
            logger.warning("策略已存在，无需重复创建, {error}".format(error=error))
            strategy_id = error.data["strategy_id"]

        multi_release_id = BscpApi.create_multi_release(
            dict(
                multi_commit_id=multi_commit_id,
                strategy_id=strategy_id,
                name=f"gsekit_release_{job_task.id}",
                **bscp_base_params,
            )
        )["multi_release_id"]
        BscpApi.publish_multi_release(dict(multi_release_id=multi_release_id, **bscp_base_params))

        data.outputs.multi_release_id = multi_release_id
        data.outputs.bscp_base_params = bscp_base_params

        return self.return_data(result=True)

    def _schedule(self, data, parent_data, callback_data=None) -> Dict:
        job_task_ids = data.get_one_of_inputs("job_task_ids")
        multi_release_id = data.get_one_of_outputs("multi_release_id")
        bscp_base_params = data.get_one_of_outputs("bscp_base_params")
        bscp_app_id = bscp_base_params["app_id"]

        bscp_cfg_id_map = {
            bscp_config.cfg_id: bscp_config for bscp_config in BscpConfig.objects.filter(app_id=bscp_app_id)
        }
        releases = BscpApi.get_multi_release(dict(multi_release_id=multi_release_id, **bscp_base_params))
        release_meta_data = releases.get("metadatas") or []
        release_id_map = defaultdict(
            lambda: {
                "job_task_status": defaultdict(lambda: {"effect_code": EffectCode.PENDING, "effect_msg": ""}),
                "release_effect_code": EffectCode.PENDING,
            }
        )

        job_task_map = defaultdict(list)
        for job_task in JobTask.objects.filter(id__in=job_task_ids):
            host = job_task.extra_data["process_info"]["host"]
            default_effect_code = EffectCode.PENDING
            effect_msg = ""

            for release in release_meta_data:
                release_id_map[release["release_id"]]["cfg_id"] = release["cfg_id"]
                release_id_map[release["release_id"]]["job_task_status"][job_task.id] = {
                    "effect_code": default_effect_code,
                    "effect_msg": effect_msg,
                }
            for config_inst in job_task.extra_data["config_instances"]:
                job_task_map[f'{host["bk_cloud_id"]}-{host["bk_host_innerip"]}-{config_inst["path"]}'].append(job_task)

        # 此处，release_id_map 通常只有一个对象
        for release_id, release in release_id_map.items():
            if release["release_effect_code"] == EffectCode.PENDING:
                effected_results = batch_request(
                    BscpApi.get_effected_app_instance_list,
                    dict(
                        cfg_id=release["cfg_id"],
                        release_id=release_id,
                        timeout_sec=RELEASE_TIMEOUT_SEC,
                        **bscp_base_params,
                    ),
                    get_count=lambda x: x["total_count"],
                    limit=MAX_PAGE_LIMIT,
                )
                release_effect_code_set = set()
                for job_task_id, job_task_status in release["job_task_status"].items():

                    for effected_result in effected_results:
                        bscp_config = bscp_cfg_id_map[effected_result["cfg_id"]]
                        path = bscp_config.path
                        job_tasks = job_task_map[f'{effected_result["cloud_id"]}-{effected_result["ip"]}-{path}']
                        for job_task in job_tasks:
                            if job_task_id != job_task.id:
                                continue

                            effect_code = effected_result.get("effect_code", EffectCode.PENDING)
                            if effect_code != EffectCode.PENDING:
                                to_be_updated_status = (
                                    JobStatus.SUCCEEDED if effect_code == EffectCode.SUCCEEDED else JobStatus.FAILED
                                )
                                release_id_map[release_id]["job_task_status"][job_task_id]["effect_code"] = effect_code
                                if to_be_updated_status == job_task.status:
                                    continue

                                job_task.set_status(to_be_updated_status)
                                # 更新已部署状态
                                if job_task.status == JobStatus.SUCCEEDED:
                                    bk_process_id = job_task.extra_data["process_info"]["process"]["bk_process_id"]
                                    inst_id = job_task.extra_data["inst_id"]
                                    ConfigInstance.objects.filter(
                                        bk_process_id=bk_process_id,
                                        inst_id=inst_id,
                                        is_latest=True,
                                        path=path,
                                        name=bscp_config.file_name,
                                    ).update(is_released=True)
                                else:
                                    job_task.set_status(
                                        JobStatus.FAILED,
                                        extra_data={
                                            "failed_reason": effected_result["effect_msg"],
                                            "err_code": ReleaseConfigException().code,
                                        },
                                    )

                    release_effect_code_set.add(
                        release_id_map[release_id]["job_task_status"][job_task_id]["effect_code"]
                    )

                # 存在pending的状态，则继续查询
                if EffectCode.PENDING in release_effect_code_set:
                    continue
                # 不存在pending的状态，则设置总的状态
                # 只要不是全部成功，则视为该release都失败
                release["release_effect_code"] = (
                    EffectCode.SUCCEEDED if ({EffectCode.SUCCEEDED} == release_effect_code_set) else EffectCode.FAILED
                )

        all_release_effect_code_set = set([release["release_effect_code"] for release in release_id_map.values()])
        if EffectCode.PENDING in all_release_effect_code_set:
            # 数据未完全上报，等待下一次轮询
            return self.return_data(result=True, is_finished=False)

        # 全部release都已上报
        result = {EffectCode.SUCCEEDED} == all_release_effect_code_set
        return self.return_data(result=result, is_finished=True)

    def inputs_format(self):
        return super().inputs_format() + [
            JobTaskBaseService.InputItem(name="job_task_ids", key="job_task_ids", required=True)
        ]


class CommitAndReleaseComponent(Component):
    name = "CommitAndReleaseComponent"
    code = "commit_and_release"
    bound_service = CommitAndReleaseService


class UploadContentComponent(Component):
    name = "UploadContentComponent"
    code = "upload_content"
    bound_service = UploadContentService


class BulkUploadContentService(MultiJobTaskBaseService):
    """
    上传文件内容 -> BSCP -> 制品库
    """

    def _execute(self, data, parent_data):
        job_tasks = data.get_one_of_inputs("job_tasks")

        is_all_success = True

        job_tasks_config_template_ids_map = JobTask.get_job_tasks_config_template_ids_map(job_tasks)

        upload_params_list = []
        get_procattr_params_list = []
        app_biz_procattr_map = defaultdict(list)

        succeeded_job_task_ids = []
        procattr_job_task_map = {}
        for job_task in job_tasks:

            inst_id = job_task.extra_data["inst_id"]

            process_info = job_task.extra_data["process_info"]
            process_obj = Process.generate_process_obj(
                bk_process_id=process_info["process"]["bk_process_id"],
                process_template_id=process_info["process_template"].get("id") or 0,
            )
            bscp_app = bscp_adapter.get_or_create_app(
                process_info["process"]["bk_biz_id"],
                process_obj["process_object_type"],
                process_obj["process_object_id"],
            )
            bscp_base_params = {"biz_id": str(bscp_app.biz_id), "app_id": bscp_app.app_id}
            get_procattr_params_list.append(bscp_base_params)

            config_template_ids = job_tasks_config_template_ids_map.get(job_task.id, [])
            if not config_template_ids:
                error = ProcessDoseNotBindTemplate()
                job_task.set_status(
                    JobStatus.IGNORED, extra_data={"failed_reason": str(error.message), "err_code": error.code}
                )
                continue

            # 对每个文件内容提交到制品库
            for config_instance in ConfigInstance.objects.filter(
                config_template_id__in=config_template_ids,
                bk_process_id=job_task.bk_process_id,
                is_latest=True,
                inst_id=inst_id,
            ):
                upload_params_list.append(
                    dict(
                        params={
                            "biz_id": bscp_app.biz_id,
                            "file": io.BytesIO(config_instance.content),
                            "sha256": config_instance.sha256,
                        },
                        headers={
                            "X-Bkapi-File-Content-Id": config_instance.sha256,
                            "X-Bkapi-File-Content-Overwrite": "true",
                        },
                    )
                )

                bk_host_innerip = job_task.extra_data["process_info"]["host"]["bk_host_innerip"]
                cloud_id = str(job_task.extra_data["process_info"]["host"]["bk_cloud_id"])

                app_biz_procattr_map[f"{bscp_app.app_id}-{bscp_app.biz_id}"].append(
                    {
                        "app_id": bscp_app.app_id,
                        "biz_id": bscp_app.biz_id,
                        "procattr": {
                            "ip": bk_host_innerip,
                            "cloud_id": cloud_id,
                            "path": "/",
                            "labels": {"ip": bk_host_innerip, "cloud_id": cloud_id},
                        },
                    }
                )
                procattr_job_task_map[f"{bk_host_innerip}-{cloud_id}"] = job_task

            # 走完全流程可认为此任务已成功，中间被 continue 跳过的则认为不是成功的
            succeeded_job_task_ids.append(job_task.id)

        # 批量上传文件
        request_multi_thread(BscpApi.upload_content, upload_params_list, get_data=lambda x: [])

        # 批量创建procattr
        to_be_created_procattr_param_list = []
        for app_biz, procattr_params in app_biz_procattr_map.items():
            # 按 app+biz 以每次最大请求数分组 进行请求
            paged_procattrs = [
                procattr_params[index : index + MAX_PAGE_LIMIT]
                for index in range(0, len(procattr_params), MAX_PAGE_LIMIT)
            ]
            for procattr in paged_procattrs:

                to_be_created_procattr_param_list.append(
                    {
                        "params": {
                            "app_id": procattr[0]["app_id"],
                            "biz_id": procattr[0]["biz_id"],
                            "data": [data["procattr"] for data in procattr],
                        }
                    }
                )
        batch_result = request_multi_thread(
            BscpApi.create_procattr_batch, to_be_created_procattr_param_list, get_data=lambda x: x.get("failed", [])
        )
        if batch_result:
            is_all_success = False
            # 记录失败原因
            for failed_attr in batch_result:
                labels = failed_attr["info"]["labels"]
                ip = labels.get("ip")
                cloud_id = labels.get("cloud_id")
                job_task = procattr_job_task_map.get(f"{ip}-{cloud_id}")
                if not job_task:
                    continue
                job_task.set_status(
                    JobStatus.IGNORED, extra_data={"failed_reason": str(ProcessDoseNotBindTemplate().message)}
                )
                succeeded_job_task_ids.remove(job_task.id)

        # 顺利走到这一步，则所有标记为成功的任务都设置为成功
        JobTask.objects.filter(id__in=succeeded_job_task_ids).update(status=JobStatus.SUCCEEDED)

        return self.return_data(result=is_all_success)

    def inputs_format(self):
        return super().inputs_format() + [
            JobTaskBaseService.InputItem(name="bk_biz_id", key="bk_biz_id", required=True)
        ]


class BulkUploadContentComponent(Component):
    name = "BulkUploadContentComponent"
    code = "bulk_upload_content"
    bound_service = BulkUploadContentService
