### 描述

Job任务详情

### 输入参数

| 参数名称     | 参数类型     | 必选   | 描述             |
| ------------ | ------------ | ------ | ---------------- |
| page   | [integer]    | 是      | 当前页数           |
| pagesize   | [integer]    | 是      | 分页大小，最大支持100           |


### 调用示例
```json
{
    "page":1,
    "pagesize":1
}
```

### 响应示例
```json
{
    "result": true,
    "data": {
        "list": [
            {
                "id": 23686276,
                "job_id": 425323,
                "bk_process_id": 21417551,
                "status": "ignored",
                "err_code": 4,
                "start_time": "2025-07-16 04:45:30.191057+00:00",
                "end_time": "2025-07-16 04:45:30.832273+00:00",
                "pipeline_id": "e24d43a4badb24b54bf04ab8f78171393",
                "extra_data": {
                    "inst_id": 85,
                    "err_code": 828,
                    "retryable": true,
                    "solutions": [],
                    "process_info": {
                        "set": {
                            "bk_set_id": 5044581,
                            "bk_set_env": "3",
                            "bk_set_name": "节点管理"
                        },
                        "host": {
                            "bk_host_id": 1223,
                            "bk_agent_id": "xxxxxxxxxxxxxxxxxxxxx",
                            "bk_cloud_id": 0,
                            "bk_addressing": "static",
                            "bk_host_innerip": "1.1.1.1",
                            "bk_host_innerip_v6": ""
                        },
                        "module": {
                            "bk_module_id": 5098972,
                            "bk_module_name": "GameSvr"
                        },
                        "process": {
                            "user": "root",
                            "timeout": 30,
                            "pid_file": "/data/home/gsekit_gamesvr/gamesvr_${LocalInstID}.pid",
                            "priority": 0,
                            "proc_num": 4,
                            "stop_cmd": "sh /data/home/gsekit_gamesvr/stop.sh",
                            "bind_info": null,
                            "bk_biz_id": 100605,
                            "last_time": "2025-06-19T14:37:41.404+08:00",
                            "start_cmd": "sh /data/home/gsekit_gamesvr/start.sh",
                            "work_path": "/data/home/gsekit_gamesvr/",
                            "auto_start": null,
                            "reload_cmd": null,
                            "create_time": "2025-06-19T14:37:41.404+08:00",
                            "description": "",
                            "restart_cmd": null,
                            "bk_func_name": "bash",
                            "bk_created_at": "2025-06-19T14:37:41.404+08:00",
                            "bk_created_by": "bcs_ca_transfer",
                            "bk_process_id": 21417551,
                            "bk_updated_at": "2025-06-19T14:37:41.404+08:00",
                            "bk_updated_by": null,
                            "face_stop_cmd": "sh /data/home/gsekit_gamesvr/stop.sh",
                            "bk_process_name": "game",
                            "company_proc_id": 132632452,
                            "bk_start_check_secs": 10,
                            "bk_supplier_account": "tencent",
                            "service_instance_id": 14799054,
                            "bk_start_param_regex": "gamesvr_${LocalInstID}"
                        },
                        "process_template": {
                            "id": 5007870
                        },
                        "service_instance": {
                            "id": 14799054,
                            "name": "1.1.1.1_game"
                        }
                    },
                    "failed_reason": "[GSE_ERROR-828]: 进程正在运行中，无需启动 (detail: no need to start the process bash(game_1) repeatedly that is already running)",
                    "local_inst_id": 1,
                    "topo_level_info": {
                        "bk_biz_id": 2,
                        "bk_set_id": 111,
                        "bk_host_id": 111,
                        "bk_module_id": 2222
                    }
                }
            }
        ],
        "count": 4,
        "status_counter": {
            "pending": 0,
            "running": 0,
            "succeeded": 0,
            "failed": 0,
            "ignored": 4
        }
    },
    "code": 0,
    "message": ""
}
```
