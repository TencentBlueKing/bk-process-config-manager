### 描述

任务列表

### 输入参数

| 参数名称     | 参数类型     | 必选   | 描述             |
| ------------ | ------------ | ------ | ---------------- |
| page   | [integer]    | 是      | 当前页数           |
| pagesize   | [integer]    | 是      | 分页大小，最大支持100           |


### 调用示例
```json
?page=1&pagesize=10
```

### 响应示例
```json
{
    "result": true,
    "data": {
        "count": 10,
        "list": [
            {
                "id": 425323,
                "bk_biz_id": 2,
                "expression": "*.*.*.*.432341",
                "scope": {
                    "bk_set_env": "3",
                    "is_expression": true,
                    "bk_process_ids": [
                        1234432
                    ]
                },
                "expression_scope": {
                    "bk_set_env": "3",
                    "bk_set_name": "*",
                    "bk_process_id": "1234432",
                    "bk_module_name": "*",
                    "bk_process_name": "*",
                    "service_instance_name": "*"
                },
                "job_object": "process",
                "job_action": "start",
                "status": "succeeded",
                "created_by": "xxxx",
                "is_ready": true,
                "start_time": "2025-07-10 12:45:29+0800",
                "end_time": "2025-07-10 12:45:31+0800",
                "pipeline_id": "xxxxxx",
                "task_granularity": "BIZ",
                "extra_data": {},
                "bk_app_code": "bksops"
            }
        ]
    },
    "code": 0,
    "message": ""
}
```
### 返回参数

| 参数名称     | 参数类型     | 必选   | 描述             |
| ------------ | ------------ | ------ | ---------------- |
| id   | [integer]    | 是      | JOB任务ID(供api_job_job_task接口查询详情使用)           |