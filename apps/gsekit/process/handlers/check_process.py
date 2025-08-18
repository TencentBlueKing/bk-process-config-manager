from enum import Enum
import re
import json
from typing import Any, Dict, List
import time
import base64
from collections import defaultdict
from apps.api import CCApi, JobApi
from apps.gsekit.process.models import Process, ProcessInst
from apps.gsekit.process.handlers.process import ProcessHandler
from apps.utils.batch_request import request_api_multi_thread
from apps.utils.mako_utils.render import mako_render

QUERY_CMDB_LIMIT = 500


def format_cmdb_params(data: Dict[int, set], fields: List[str]):
    params_list = []
    for biz_id, bk_ids in data.items():
        bk_ids = list(bk_ids)
        for i in range(0, len(bk_ids), QUERY_CMDB_LIMIT):
            params_list.append(
                {
                    "no_request": True,
                    "bk_biz_id": biz_id,
                    "bk_ids": bk_ids[i : i + QUERY_CMDB_LIMIT],
                    "fields": fields,
                }
            )

    return params_list


class ErrorType(Enum):
    """错误类型枚举"""

    PARSING_FAILED = "PARSING_FAILED"
    AGENT_EXCEPTION = "AGENT_EXCEPTION"
    ILLEGAL_VALUE_KEY = "ILLEGAL_VALUE_KEY"
    EXPECTATION_MISMATCH = "EXPECTATION_MISMATCH"
    OTHER = "OTHER"

    def __str__(self):
        return self.value


class ProcessCheckManager:
    """进程托管检查管理器，负责执行进程托管状态检查及错误收集"""

    # 账户别名映射（操作系统类型 -> 账户名）
    ACCOUNT_ALIAS = {"1": "root", "2": "Administrator", "3": "root"}

    # 脚本语言类型（操作系统类型 -> 语言标识）
    SCRIPT_LANGUAGE = {"1": 1, "2": 2}

    # 检查脚本内容（操作系统类型 -> 脚本命令）
    SCRIPT_CONTENT = {"1": "cat /usr/local/gse2_bkte/agent/etc/.proc", "2": "type c:\\gse2_bkte\\agent\\etc\\.proc"}

    def __init__(self, bk_biz_id):
        """初始化检查器

        Args:
            bk_biz_id: 业务ID
        """
        self.bk_biz_id = bk_biz_id
        self.contact = f"GSEKIT_BIZ_{self.bk_biz_id}"

        # 初始化数据存储结构
        self.bk_ip_cloud__host_id = {}  # {cloud_ip_key: host_id}
        self.process_template_ids = set()  # 进程模板ID集合
        self.bk_cloud__inner_ip_map = defaultdict(list)  # {cloud_id: [inner_ips]}
        self.bk_host_id__os_type_map = {}  # {host_id: os_type}
        self.bk_host_id_info = {}  # {host_id: host_detail}
        self.process_name_template_info_map = {}  # {process_name: template_info}
        self.bk_host_id_process_inst_map = defaultdict(list)  # {host_id: [proc_infos]}
        self.bk_host_procs = defaultdict(dict)  # {host_id: {valuekey: proc_detail}}
        self.error_host = []  # 错误主机列表

    def _collect_processes(self):
        """收集进程基本信息，构建云-IP映射及模板ID集合"""
        processes = Process.objects.filter(bk_biz_id=self.bk_biz_id).values(
            "process_template_id",
            "bk_cloud_id",
            "bk_host_innerip",
        )
        for process in processes:
            self.bk_cloud__inner_ip_map[process["bk_cloud_id"]].append(process["bk_host_innerip"])
            self.process_template_ids.add(process["process_template_id"])

    def _fetch_host_info(self):
        """从CC获取主机详细信息（ID、操作系统等）"""
        for bk_cloud_id, inner_ips in self.bk_cloud__inner_ip_map.items():
            # 每次处理的IP数量
            batch_size = QUERY_CMDB_LIMIT
            # 计算总共有多少批
            total_batches = (len(inner_ips) + batch_size - 1) // batch_size

            for batch in range(total_batches):
                # 计算当前批次的IP切片
                start_idx = batch * batch_size
                end_idx = start_idx + batch_size
                current_ips = inner_ips[start_idx:end_idx]

                # 构造CC查询参数，使用当前批次的IP
                cc_kwargs = {
                    "no_request": True,
                    "fields": ["bk_host_id", "bk_cloud_id", "bk_host_innerip", "bk_os_type"],
                    "bk_biz_id": self.bk_biz_id,
                    "host_property_filter": {
                        "condition": "AND",
                        "rules": [
                            {"field": "bk_host_innerip", "operator": "in", "value": current_ips},
                            {"field": "bk_cloud_id", "operator": "equal", "value": bk_cloud_id},
                        ],
                    },
                    "page": {"limit": QUERY_CMDB_LIMIT, "start": 0},
                }

                # 调用CC API获取当前批次主机信息
                ret = CCApi.list_biz_hosts(cc_kwargs)
                for host in ret["info"]:
                    cloud_ip_key = f"{host['bk_cloud_id']}_{host['bk_host_innerip']}"
                    self.bk_ip_cloud__host_id[cloud_ip_key] = host["bk_host_id"]
                    self.bk_host_id__os_type_map[host["bk_host_id"]] = host["bk_os_type"]
                    self.bk_host_id_info[host["bk_host_id"]] = host

    def _fetch_process_templates(self):
        """获取进程模板信息，构建进程名-模板映射"""
        if not self.process_template_ids:
            return
        process_template_info_list = ProcessHandler(self.bk_biz_id).bulk_process_template(
            list(self.process_template_ids)
        )
        self.process_name_template_info_map = {pt["bk_process_name"]: pt for pt in process_template_info_list}

    def _process_process_insts(self):
        """处理进程实例，生成预期进程信息"""
        process_insts = ProcessInst.objects.filter(bk_biz_id=self.bk_biz_id).values()
        biz_module_map = defaultdict(set)
        for inst in process_insts:
            biz_module_map[inst["bk_biz_id"]].add(inst["bk_module_id"])

        bk_module_params: List[Dict[str, Any]] = format_cmdb_params(
            biz_module_map, fields=["bk_module_id", "bk_module_name"]
        )

        module_id_name_map: Dict[int, str] = {}

        module_id_name_map: Dict[int, str] = {
            module["bk_module_id"]: module["bk_module_name"]
            for module in request_api_multi_thread(CCApi.find_module_batch, bk_module_params)
        }

        for inst in process_insts:
            cloud_ip_key = f"{inst['bk_cloud_id']}_{inst['bk_host_innerip']}"
            host_id = self.bk_ip_cloud__host_id.get(cloud_ip_key)
            if not host_id:
                self._add_error([host_id], ErrorType.OTHER, f"{cloud_ip_key}未查询到主机信息", "请联系管理员确认")
                continue

            # 构建模板渲染上下文
            context = {
                "inst_id": inst["inst_id"],
                "inst_id_0": inst["inst_id"] - 1,
                "local_inst_id": inst["local_inst_id"],
                "local_inst_id0": inst["local_inst_id"] - 1,
                "bk_process_name": inst["bk_process_name"],
                # 兼容老版本字段
                "InstID": inst["inst_id"],
                "InstID0": inst["inst_id"] - 1,
                "LocalInstID": inst["local_inst_id"],
                "LocalInstID0": inst["local_inst_id"] - 1,
                "FuncID": inst["bk_process_name"],
                # "SetName": set_id_name_map.get(inst["bk_set_id"]),
                "ModuleName": module_id_name_map.get(inst["bk_module_id"]),
            }

            # 生成进程预期信息
            local_inst_name = f"{inst['bk_process_name']}_{inst['local_inst_id']}"
            template_info = self.process_name_template_info_map.get(inst["bk_process_name"])
            if not template_info:
                self._add_error(
                    [host_id],
                    ErrorType.OTHER,
                    f"local_inst_name:{local_inst_name}, 未找到进程模板信息",
                    "请检查进程模板是否正常配置, 如无需要管理此进程可忽略",
                )
                continue

            proc_info = {
                "is_auto": inst["is_auto"],
                "procName": template_info["property"]["bk_func_name"],
                "setupPath": mako_render(template_info["property"]["work_path"] or "", context),
                "pidPath": mako_render(template_info["property"]["pid_file"] or "", context),
                "contact": self.contact,
                "startCmd": mako_render(template_info["property"].get("start_cmd") or "", context),
                "stopCmd": mako_render(template_info["property"].get("stop_cmd") or "", context),
                "restartCmd": mako_render(template_info["property"].get("restart_cmd") or "", context),
                "reloadCmd": mako_render(template_info["property"].get("reload_cmd") or "", context),
                "killCmd": mako_render(template_info["property"].get("face_stop_cmd") or "", context),
                "versionCmd": mako_render(template_info["property"].get("version_cmd") or "", context),
                "healthCmd": mako_render(template_info["property"].get("health_cmd") or "", context),
                "valuekey": f"{self.contact}:{local_inst_name}",
            }
            self.bk_host_id_process_inst_map[host_id].append(proc_info)

    def _execute_scripts_and_parse(self):
        """按操作系统类型执行检查脚本并解析结果"""
        # 构建操作系统-主机ID映射
        os_type_host_map = defaultdict(list)
        for host_id, os_type in self.bk_host_id__os_type_map.items():
            os_type_host_map[os_type].append(host_id)

        for os_type, host_ids in os_type_host_map.items():
            # 构造脚本执行参数
            job_kwargs = {
                "no_request": True,
                "task_name": f"GSEKIT_CHECK_PROC_INFO_{os_type.upper()}",
                "bk_scope_type": "biz",
                "bk_scope_id": self.bk_biz_id,
                "script_language": self.SCRIPT_LANGUAGE[str(os_type)],
                "script_content": base64.b64encode(self.SCRIPT_CONTENT[str(os_type)].encode("utf8")).decode("utf8"),
                "account_alias": self.ACCOUNT_ALIAS[str(os_type)],
                "target_server": {"host_id_list": host_ids},
            }

            # 执行脚本
            try:
                execute_result = JobApi.fast_execute_script(job_kwargs)
            except Exception as e:
                self._add_error(host_ids, ErrorType.OTHER, f"脚本执行失败: {str(e)}", "请参考错误信息提示，如有问题请联系管理员")
                continue

            status_kwargs = {
                "no_request": True,
                "bk_scope_type": "biz",
                "bk_scope_id": self.bk_biz_id,
                "job_instance_id": execute_result["job_instance_id"],
            }
            is_finished = False
            while not is_finished:
                status_result = JobApi.get_job_instance_status(status_kwargs)
                if not status_result["finished"]:
                    time.sleep(5)
                is_finished = status_result["finished"]

            # 获取执行日志
            log_kwargs = {
                "no_request": True,
                "bk_scope_type": "biz",
                "bk_scope_id": self.bk_biz_id,
                "job_instance_id": execute_result["job_instance_id"],
                "step_instance_id": execute_result["step_instance_id"],
                "host_id_list": host_ids,
            }

            try:
                ip_logs = JobApi.batch_get_job_instance_ip_log(log_kwargs)
            except Exception as e:
                self._add_error(host_ids, ErrorType.OTHER, f"日志获取失败: {str(e)}", "请参考错误信息提示，如有问题请联系管理员")
                continue

            # 解析日志内容
            self._parse_ip_logs(ip_logs["script_task_logs"])

            # 处理无日志的主机
            logged_host_ids = {log["host_id"] for log in ip_logs["script_task_logs"]}
            no_log_hosts = set(host_ids) - logged_host_ids
            for host_id in no_log_hosts:
                self._add_error_item(
                    host_id=host_id,
                    error_type=ErrorType.PARSING_FAILED,
                    error_msg="进程信息解析失败，检查Agent是否正常",
                    handling_suggestion="请检查Agent是否正常运行",
                )

    def _parse_ip_logs(self, script_task_logs):
        """解析IP日志，提取进程信息"""
        for log in script_task_logs:
            host_id = log["host_id"]
            try:
                # 提取JSON内容
                json_str = re.search(r"\{.*\}", log["log_content"], re.DOTALL).group()
                proc_data = json.loads(json_str).get("proc", [])

                # 存储进程信息
                for proc in proc_data:
                    if proc.get("contact") == self.contact:
                        self.bk_host_procs[host_id][proc["valuekey"]] = proc

            except Exception:
                # 处理解析错误
                error_msg = f"进程信息解析失败: {log['log_content']}"
                handling_suggestion = "请根据错误信息提示进行相应处理"
                if "agent not available" in error_msg:
                    error_type = ErrorType.AGENT_EXCEPTION
                else:
                    error_type = ErrorType.PARSING_FAILED
                self._add_error_item(host_id, error_type, error_msg, handling_suggestion)

    def _check_process_mismatch(self):
        """检查进程实际信息与预期是否匹配"""
        for host_id, proc_infos in self.bk_host_id_process_inst_map.items():
            # 跳过已记录错误的主机
            if any(e["host_id"] == host_id for e in self.error_host):
                continue

            # 检查非法valuekey
            expected_keys = {proc["valuekey"] for proc in proc_infos}
            actual_keys = set(self.bk_host_procs.get(host_id, {}).keys())
            illegal_keys = actual_keys - expected_keys
            if illegal_keys:
                self._add_error_item(
                    host_id=host_id,
                    error_type=ErrorType.ILLEGAL_VALUE_KEY,
                    error_msg=f"存在非法valuekey托管信息: {illegal_keys}",
                    handling_suggestion="请检查进程托管配置, 可尝试取消托管再重新托管, 如问题依然存在, 请联系管理员确认",
                )
                continue

            # 检查每个进程的匹配情况
            for proc in proc_infos:
                self._check_single_proc(host_id, proc)

    def _check_single_proc(self, host_id, proc):
        """检查单个进程的信息匹配性"""
        is_auto = proc.pop("is_auto")
        actual_proc = self.bk_host_procs.get(host_id, {}).get(proc["valuekey"])

        if not is_auto:
            # 未托管不应有托管信息
            if actual_proc:
                self._add_error_item(
                    host_id=host_id,
                    error_type=ErrorType.EXPECTATION_MISMATCH,
                    error_msg=f"进程未托管但获取到信息: {actual_proc}",
                    handling_suggestion="请检查进程托管配置, 可尝试取消托管再重新托管",
                )
            return

        # 已托管必须有托管信息
        if not actual_proc:
            self._add_error_item(
                host_id=host_id,
                error_type=ErrorType.EXPECTATION_MISMATCH,
                error_msg=f"进程已托管但未获取到信息: {proc['valuekey']}",
                handling_suggestion="请检查进程托管配置, 可尝试重新托管",
            )
            return

        # 检查属性匹配
        if not proc.items() <= actual_proc.items():
            diff = dict(set(proc.items()) - set(actual_proc.items()))
            self._add_error_item(
                host_id=host_id,
                error_type=ErrorType.EXPECTATION_MISMATCH,
                error_msg=f"托管信息与预期不符，差异: {diff}",
                handling_suggestion="请检查进程托管配置,可尝试取消托管再重新托管",
            )

    def _add_error(self, host_ids, error_type, error_msg, handling_suggestion):
        """批量添加错误信息"""
        for host_id in host_ids:
            self._add_error_item(host_id, error_type, error_msg, handling_suggestion)

    def _add_error_item(self, host_id, error_type, error_msg, handling_suggestion):
        """添加单个错误项"""
        host_info = self.bk_host_id_info.get(host_id, {})
        self.error_host.append(
            {
                "host_id": host_id,
                "inner_ip": host_info.get("bk_host_innerip", "未知IP"),
                "bk_cloud_id": host_info.get("bk_cloud_id", "未知云区域"),
                "error_type": str(error_type),
                "error_msg": error_msg,
                "handling_suggestion": handling_suggestion,
            }
        )

    def run(self):
        """执行完整检查流程"""
        self._collect_processes()
        self._fetch_host_info()
        self._fetch_process_templates()
        self._process_process_insts()
        self._execute_scripts_and_parse()
        self._check_process_mismatch()

        return self.error_host


# 执行示例
if __name__ == "__main__":
    bk_biz_id = 815  # 业务ID
    checker = ProcessCheckManager(bk_biz_id)
    checker.run()
