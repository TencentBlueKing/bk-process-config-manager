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
import json
import logging
from typing import Dict

from django.db.models import F
from django.utils.translation import ugettext as _
from pipeline.component_framework.component import Component
from pipeline.core.flow.activity import StaticIntervalGenerator

from apps.gsekit.job.models import JobProcInstStatusStatistics, JobTask, JobStatus
from apps.gsekit.pipeline_plugins.components.collections.base import (
    JobTaskBaseService,
    GSE_POLLING_INTERVAL as POLLING_INTERVAL,
    MultiJobTaskBaseService,
)
from apps.gsekit.process.exceptions import ProcessAttrIsNotConfiguredException
from apps.gsekit.process.models import Process, ProcessInst
from apps.utils.mako_utils.render import mako_render
from dataclasses import dataclass
from .base import CommonData
from apps.adapters.api.gse import get_gse_api_helper
from apps.adapters.api.gse.base import GseApiBaseHelper

logger = logging.getLogger("app")

NAMESPACE = "GSEKIT_BIZ_{bk_biz_id}"


class GseOpType(object):
    """
    0:启动进程（start）,调用spec.control中的start_cmd启动进程，启动成功会注册托管；
    1:停止进程（stop）, 调用spec.control中的stop_cmd启动进程，停止成功会取消托管；
    2:进程状态查询；
    3:注册托管进程，令gse_agent对该进程进行托管（托管：当托管进程异常退出时，agent会自动拉起托管进程；当托管进程资源超限时，agent会杀死托管进程）；
    4:取消托管进程，令gse_agent对该进程不再托管；
    7:重启进程（restart）,调用spec.control中的restart_cmd启动进程；
    8:重新加载进程（reload）,调用spec.control中的reload_cmd启动进程；
    9:杀死进程（kill）,调用spec.control中的kill_cmd启动进程，杀死成功会取消托管
    """

    START = 0
    STOP = 1
    CHECK = 2
    SET_AUTO = 3
    UNSET_AUTO = 4
    RESTART = 7
    RELOAD = 8
    FORCE_STOP = 9


class GseAutoType(object):
    """
    0:周期执行进程
    1:常驻进程
    2:单次执行进程
    """

    SCHEDULE = 0
    RESIDENT = 1
    ONCE = 2


class GseDataErrorCode(object):
    SUCCESS = 0
    RUNNING = 115
    AGENT_NOT_FIND = 117
    PROC_RUNNING = 828
    PROC_NO_RUNNING = 829
    UNKNOWN_OP_TYPE = 832
    POST_CHECK_ERROR = 836
    ALREADY_REGISTERED = 850
    OP_FAILED = 65535

    @classmethod
    def need_ignore_err_code(cls, op_type: int, error_code: int) -> bool:
        # 对运行中的进程执行【启动】命令，结果是执行失败（不能忽略），业务需要全stop后再重新start
        # （主要考量的点在于进程、配置会有更新遗漏导致最终没有生效的风险）
        # if op_type == GseOpType.START and error_code == cls.PROC_RUNNING:
        #     # 启动进程，但进程本身已运行中
        #     return True

        # 对于已停止的进程执行【停止】命令，结果是执行成功，已停止的进程实例可以标记成忽略
        if op_type == GseOpType.STOP and error_code == cls.PROC_NO_RUNNING:
            # 停止进程，但进程本身未运行
            return True

        # 其它场景不需要忽略
        return False


GSE_RUNNING_TASK_CODE = 1000115


GSE_OP_ERROR_CODE_MSG_MAP = {
    GseDataErrorCode.RUNNING: _("进程操作正在执行"),
    GseDataErrorCode.AGENT_NOT_FIND: _("AGENT状态异常"),
    GseDataErrorCode.PROC_RUNNING: _("进程正在运行中，无需启动"),
    GseDataErrorCode.PROC_NO_RUNNING: _("进程当前未运行，无需停止"),
    GseDataErrorCode.UNKNOWN_OP_TYPE: _("操作类型非法"),
    # 进程停止失败（后置检查状态为运行中）
    GseDataErrorCode.POST_CHECK_ERROR: _("进程启动失败（后置检查状态为未运行）"),
    GseDataErrorCode.OP_FAILED: _("进程操作命令执行失败，命令打屏信息参考error_msg"),
}

# 进程操作成功后的进程状态映射
OP_SUCCESS_PROC_STATUS_MAP = {
    GseOpType.START: Process.ProcessStatus.RUNNING,
    GseOpType.STOP: Process.ProcessStatus.TERMINATED,
    # 设置托管和取消托管并不能确定进程状态，这种场景无需修改状态
    # GseOpType.SET_AUTO: Process.ProcessStatus.RUNNING,
    # GseOpType.UNSET_AUTO: Process.ProcessStatus.RUNNING,
    GseOpType.RESTART: Process.ProcessStatus.RUNNING,
    GseOpType.RELOAD: Process.ProcessStatus.RUNNING,
    GseOpType.FORCE_STOP: Process.ProcessStatus.TERMINATED,
}

# 进程操作成功后托管状态变化映射
OP_SUCCESS_PROC_AUTO_MAP = {
    GseOpType.STOP: False,
    GseOpType.UNSET_AUTO: False,
    GseOpType.START: True,
    GseOpType.SET_AUTO: True,
}

PROC_STATUS_NAME_MAP = {Process.ProcessStatus.RUNNING: "running", Process.ProcessStatus.TERMINATED: "terminated"}

# 操作类型对应的命令字段映射
OP_TYPE_PROCESS_ATTR_MAP = {
    GseOpType.START: [{"attr_name": _("启动命令"), "attr_key": "start_cmd"}],
    GseOpType.STOP: [{"attr_name": _("停止命令"), "attr_key": "stop_cmd"}],
    GseOpType.SET_AUTO: [{"attr_name": _("启动命令"), "attr_key": "start_cmd"}],
    GseOpType.RESTART: [{"attr_name": _("重启命令"), "attr_key": "restart_cmd"}],
    GseOpType.RELOAD: [{"attr_name": _("重载命令"), "attr_key": "reload_cmd"}],
    GseOpType.FORCE_STOP: [{"attr_name": _("强制停止命令"), "attr_key": "face_stop_cmd"}],
}
# 所有操作都补充 工作路径、启动用户、PID路径的检查
for _op_type, attrs in OP_TYPE_PROCESS_ATTR_MAP.items():
    OP_TYPE_PROCESS_ATTR_MAP[_op_type].extend(
        [
            {"attr_name": _("工作路径"), "attr_key": "work_path"},
            {"attr_name": _("PID 文件路径"), "attr_key": "pid_file"},
            {"attr_name": _("启动用户"), "attr_key": "user"},
        ]
    )

# 参数缺省值
DEFAULT_START_CHECK_SECS = 5
DEFAULT_OP_TIMEOUT = 60


@dataclass
class GseCommonData(CommonData):
    gse_api_helper: GseApiBaseHelper


class GseCommonService(MultiJobTaskBaseService):
    @classmethod
    def get_common_data(cls, data) -> GseCommonData:
        common_data = super().get_common_data(data)
        return GseCommonData(
            gse_version=common_data.gse_version,
            gse_api_helper=get_gse_api_helper(gse_version=common_data.gse_version),
        )


class BulkGseOperateProcessService(GseCommonService):
    """
    GSE Service 基类
    """

    __need_schedule__ = True
    interval = StaticIntervalGenerator(POLLING_INTERVAL)

    @staticmethod
    def is_op_cmd_configured(op_type, process_info, raise_exception: bool = False):
        """判断操作是否已配置对应命令"""
        process_attrs = OP_TYPE_PROCESS_ATTR_MAP.get(op_type) or []
        for process_attr in process_attrs:
            if process_info.get(process_attr["attr_key"]):
                continue
            if raise_exception:
                raise ProcessAttrIsNotConfiguredException(
                    process_name=f'{process_info.get("bk_func_name")}-{process_info.get("bk_process_name")}',
                    process_attr=f'{process_attr["attr_name"]}({process_attr["attr_key"]})',
                )
            else:
                return False

        return True

    @classmethod
    def get_job_task_gse_result(cls, gse_api_result: Dict[str, Dict], job_task: JobTask, common_data) -> Dict:
        """GSE接口偶尔会出现IP进程不返回的情况，针对这种情况默认填充 GseDataErrorCode.RUNNING 状态"""
        host_info = job_task.extra_data["process_info"]["host"]
        process_info = job_task.extra_data["process_info"]["process"]
        local_inst_id = job_task.extra_data["local_inst_id"]
        namespace = NAMESPACE.format(bk_biz_id=process_info["bk_biz_id"])
        uniq_key = common_data.gse_api_helper.get_gse_proc_key(
            host_info, namespace, f"{process_info['bk_process_name']}_{local_inst_id}"
        )
        return gse_api_result["data"].get(uniq_key) or {
            "content": "",
            "error_code": GseDataErrorCode.RUNNING,
            "error_msg": "handling",
        }

    @classmethod
    def increment_inst_status_count(cls, job_task: JobTask, status: int, is_auto: bool):
        increment_status_field = f"proc_inst_{PROC_STATUS_NAME_MAP[status]}_num"
        increment_auto_field = f"proc_inst_{'auto' if is_auto else 'noauto'}_num"

        update_params = {
            increment_auto_field: F(increment_auto_field) + 1,
            increment_status_field: F(increment_status_field) + 1,
        }
        # 查出 ID 再更新，避免按 job_id where..update 的情况下多行加锁导致死锁
        statistics_id = JobProcInstStatusStatistics.objects.get(
            job_id=job_task.job_id, bk_process_id=job_task.bk_process_id
        ).id
        JobProcInstStatusStatistics.objects.filter(id=statistics_id).update(**update_params)

    @classmethod
    def sync_status_to_proc(cls, job_task: JobTask):
        statistics = JobProcInstStatusStatistics.objects.get(
            job_id=job_task.job_id, bk_process_id=job_task.bk_process_id
        )

        update_params = {}
        # 出现失败时整体进程状态为失败
        if statistics.proc_inst_terminated_num > 0:
            update_params["process_status"] = Process.ProcessStatus.TERMINATED
        elif statistics.proc_inst_total_num == statistics.proc_inst_running_num:
            update_params["process_status"] = Process.ProcessStatus.RUNNING

        # 出现托管时，整体未托管
        if statistics.proc_inst_noauto_num > 0:
            update_params["is_auto"] = False
        elif statistics.proc_inst_total_num == statistics.proc_inst_auto_num:
            update_params["is_auto"] = True

        logger.info(
            f"sync_status_to_proc[job_task:{job_task.id}, bk_process_id:{job_task.bk_process_id}]-{update_params}"
        )
        if update_params:
            Process.objects.filter(bk_process_id=job_task.bk_process_id).update(**update_params)

    @classmethod
    def generate_proc_op_error_msg(cls, error_code: int, error_msg: str) -> str:
        simple_msg = GSE_OP_ERROR_CODE_MSG_MAP.get(error_code, _("参考返回的error_code和error_msg"))
        if error_code == GseDataErrorCode.POST_CHECK_ERROR and error_msg.startswith("stop"):
            simple_msg = _("进程停止失败（后置检查状态为运行中）")

        return _("[GSE_ERROR-{error_code}]: {simple_msg} (detail: {error_msg})").format(
            error_code=error_code, simple_msg=simple_msg, error_msg=error_msg
        )

    def _execute(self, data, parent_data, common_data):
        job_tasks = data.get_one_of_inputs("job_tasks")
        op_type = data.get_one_of_inputs("op_type")
        data.outputs.proc_op_status_map = {}

        proc_operate_req = []
        for job_task in job_tasks:

            host_info = job_task.extra_data["process_info"]["host"]
            process_info = job_task.extra_data["process_info"]["process"]
            set_info = job_task.extra_data["process_info"]["set"]
            module_info = job_task.extra_data["process_info"]["module"]
            inst_id = job_task.extra_data["inst_id"]
            local_inst_id = job_task.extra_data["local_inst_id"]

            context = {
                "inst_id": inst_id,
                "inst_id_0": inst_id - 1,
                "local_inst_id": local_inst_id,
                "local_inst_id0": local_inst_id - 1,
                "bk_set_name": set_info["bk_set_name"],
                "bk_module_name": module_info["bk_module_name"],
                "bk_process_name": process_info["bk_process_name"],
                # 兼容老版本字段
                "InstID": inst_id,
                "InstID0": inst_id - 1,
                "LocalInstID": local_inst_id,
                "LocalInstID0": local_inst_id - 1,
                "SetName": set_info["bk_set_name"],
                "ModuleName": module_info["bk_module_name"],
                "FuncID": process_info["bk_process_name"],
            }
            self.is_op_cmd_configured(op_type, process_info, raise_exception=True)

            proc_operate_req.append(
                {
                    "meta": {
                        "namespace": NAMESPACE.format(bk_biz_id=process_info["bk_biz_id"]),
                        "name": f"{process_info['bk_process_name']}_{local_inst_id}",
                        "labels": {
                            "bk_process_name": process_info["bk_process_name"],
                            "bk_process_id": process_info["bk_process_id"],
                        },
                    },
                    "op_type": op_type,
                    "hosts": [
                        {
                            "bk_host_innerip": host_info["bk_host_innerip"],
                            "bk_cloud_id": host_info["bk_cloud_id"],
                            "bk_agent_id": host_info.get("bk_agent_id", ""),
                        }
                    ],
                    "spec": {
                        "identity": {
                            "index_key": "",
                            "proc_name": process_info["bk_func_name"],
                            "setup_path": mako_render(process_info["work_path"] or "", context),
                            "pid_path": mako_render(process_info["pid_file"] or "", context),
                            "user": process_info["user"],
                        },
                        "control": {
                            "start_cmd": mako_render(process_info["start_cmd"] or "", context),
                            "stop_cmd": mako_render(process_info["stop_cmd"] or "", context),
                            "restart_cmd": mako_render(process_info["restart_cmd"] or "", context),
                            "reload_cmd": mako_render(process_info["reload_cmd"] or "", context),
                            "kill_cmd": mako_render(process_info["face_stop_cmd"] or "", context),
                        },
                        "alive_monitor_policy": {
                            "auto_type": GseAutoType.RESIDENT,
                            # 缺省取gse接口设定的默认值
                            "start_check_secs": process_info.get("bk_start_check_secs") or DEFAULT_START_CHECK_SECS,
                            "op_timeout": process_info.get("timeout") or DEFAULT_OP_TIMEOUT,
                        },
                    },
                }
            )
            # pipeline-engine会把data转为json，不能用int作为key
            data.outputs.proc_op_status_map[str(job_task.id)] = GseDataErrorCode.RUNNING
        task_id = common_data.gse_api_helper.operate_proc_multi(proc_operate_req=proc_operate_req)

        data.outputs.task_id = task_id
        return self.return_data(result=True)

    def _schedule(self, data, parent_data, common_data, callback_data=None):
        job_tasks = data.get_one_of_inputs("job_tasks")
        op_type = data.get_one_of_inputs("op_type")
        task_id = data.get_one_of_outputs("task_id")
        gse_api_result = common_data.gse_api_helper.get_proc_operate_result(task_id)
        if gse_api_result["code"] == GSE_RUNNING_TASK_CODE:
            # 查询的任务等待执行中，还未入到redis，继续下一次查询
            return self.return_data(result=True)

        for job_task in job_tasks:
            local_inst_id = job_task.extra_data["local_inst_id"]
            task_result = self.get_job_task_gse_result(gse_api_result, job_task, common_data)
            error_code = task_result.get("error_code")

            # 已处理过的任务
            if data.outputs.proc_op_status_map[str(job_task.id)] == error_code:
                continue

            data.outputs.proc_op_status_map[str(job_task.id)] = error_code

            if error_code == GseDataErrorCode.SUCCESS:
                process_inst = ProcessInst.objects.get(
                    bk_process_id=job_task.bk_process_id, local_inst_id=local_inst_id
                )
                # 操作成功，将进程更新到相应操作后的期望状态
                process_status = OP_SUCCESS_PROC_STATUS_MAP.get(op_type, process_inst.process_status)
                is_auto = OP_SUCCESS_PROC_AUTO_MAP.get(op_type, process_inst.is_auto)
                # 变更才进行更新，减少DB操作
                if process_status != process_inst.process_status or is_auto != process_inst.is_auto:
                    process_inst.process_status = process_status
                    process_inst.is_auto = is_auto
                    process_inst.save(update_fields=["is_auto", "process_status"])

                # 更新进程关联实例托管及状态统计
                self.increment_inst_status_count(job_task, process_inst.process_status, process_inst.is_auto)
                # 操作成功时inst状态立即变更，无需经过GseCheckProcessService查询状态，此时需要同步状态到Process
                self.sync_status_to_proc(job_task)

                # 设置任务成功
                job_task.set_status(JobStatus.SUCCEEDED)

            elif error_code != GseDataErrorCode.RUNNING:
                # 操作失败，进入下一个原子查询并更新进程状态
                error_msg = task_result.get("error_msg")
                if GseDataErrorCode.need_ignore_err_code(op_type=op_type, error_code=error_code):
                    job_status = JobStatus.IGNORED
                else:
                    job_status = JobStatus.FAILED
                job_task.set_status(
                    job_status,
                    extra_data={
                        "failed_reason": self.generate_proc_op_error_msg(error_code, error_msg),
                        "err_code": error_code,
                    },
                )

        # 还有未完成的任务
        if GseDataErrorCode.RUNNING in data.outputs.proc_op_status_map.values():
            return self.return_data(result=True)

        # 部分失败、全部失败、全部成功，都进入下个 CheckProcess 原子
        return self.return_data(result=True, is_finished=True)

    def inputs_format(self):
        return super().inputs_format() + [
            MultiJobTaskBaseService.InputItem(name="op_type", key="op_type", required=True)
        ]

    def outputs_format(self):
        return [
            # 当前原子进程操作状态码
            MultiJobTaskBaseService.OutputItem(name="proc_op_status_map", key="proc_op_status_map", type="dict"),
        ] + super().outputs_format()


class BulkGseCheckProcessService(BulkGseOperateProcessService):
    def _execute(self, data, parent_data, common_data):
        # 上一个原子进程操作不是成功或忽略的情况，需要进一步查询进程实际的运行状态
        for job_task in data.get_one_of_inputs("job_tasks"):
            if job_task.status not in [JobStatus.SUCCEEDED, JobStatus.IGNORED]:
                return super()._execute(data, parent_data, common_data)

        # 上一个原子进程操作都成功或忽略了，无需查询进程状态, 也无需更新job_task，直接跳过此原子
        self.finish_schedule()
        return self.return_data(result=True)

    def _schedule(self, data, parent_data, common_data, callback_data=None):

        job_tasks = data.get_one_of_inputs("job_tasks")
        task_id = data.get_one_of_outputs("task_id")

        if not task_id:
            # 兼容新版引擎，TODO 待优化，在 execute 处提前 finish_schedule
            return self.return_data(result=True, is_finished=True)

        gse_api_result = common_data.gse_api_helper.get_proc_operate_result(task_id)
        if gse_api_result["code"] == GSE_RUNNING_TASK_CODE:
            # 查询的任务等待执行中，还未入到redis，继续下一次查询
            return self.return_data(result=True)

        for job_task in job_tasks:
            local_inst_id = job_task.extra_data["local_inst_id"]
            task_result = self.get_job_task_gse_result(gse_api_result, job_task, common_data)
            error_code = task_result.get("error_code")

            if error_code == GseDataErrorCode.SUCCESS:
                gse_ip_proc_info = json.loads(task_result["content"])
                try:
                    pid = gse_ip_proc_info["process"][0]["instance"][0]["pid"]
                    is_auto = gse_ip_proc_info["process"][0]["instance"][0]["isAuto"]
                except (KeyError, IndexError):
                    pid = -1
                    is_auto = False
                # pid < 0 表示进程终止
                process_status = Process.ProcessStatus.TERMINATED if pid < 0 else Process.ProcessStatus.RUNNING
                # 更新进程状态
                ProcessInst.objects.filter(bk_process_id=job_task.bk_process_id, local_inst_id=local_inst_id).update(
                    process_status=process_status, is_auto=is_auto
                )

                self.increment_inst_status_count(job_task, process_status, is_auto)
                self.sync_status_to_proc(job_task)

        if GseDataErrorCode.RUNNING in set([result["error_code"] for key, result in gse_api_result["data"].items()]):
            # RUNNING 进入下一次轮询
            return self.return_data(result=True)

        job_tasks_status_set = {job_task.status for job_task in job_tasks}

        return self.return_data(
            result=job_tasks_status_set.issubset({JobStatus.SUCCEEDED, JobStatus.IGNORED}), is_finished=True
        )

    def inputs_format(self):
        return super().inputs_format() + [
            # 上一个原子进程操作状态码，不传或操作失败都会查询并更新进程状态
            JobTaskBaseService.InputItem(name="last_proc_op_status_map", key="last_proc_op_status_map", required=False)
        ]


class BulkGseOperateProcessComponent(Component):
    name = "BulkGseOperateProcessComponent"
    code = "bulk_gse_operate_process"
    bound_service = BulkGseOperateProcessService


class BulkGseCheckProcessComponent(Component):
    name = "BulkGseCheckProcessComponent"
    code = "bulk_gse_check_process"
    bound_service = BulkGseCheckProcessService
