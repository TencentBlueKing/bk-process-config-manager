import chalk from 'chalk'

import { sleep } from './util'

export async function response (getArgs, postArgs, req) {
    console.log(chalk.cyan('req', req.method))
    console.log(chalk.cyan('getArgs', JSON.stringify(getArgs, null, 0)))
    console.log(chalk.cyan('postArgs', JSON.stringify(postArgs, null, 0)))
    console.log()

    const delay = getArgs.delay || 800
    delay && await sleep(delay)

    const invoke = getArgs.invoke
    if (invoke === 'example') {
        return {
            code: 0,
            result: true,
            data: {
                text: 'Hello World!'
            },
            message: 'ok'
        }
    }
    if (invoke === 'getTaskHistoryList') {
        return {
            code: 0,
            result: true,
            data: [
                {
                    ID: '1200',
                    job_object_choices: '配置文件',
                    job_action_choices: '启动',
                    bk_opera_range: '****************',
                    bk_per_account: 'admin',
                    bk_start_time: '2020-07-05 08:09:08',
                    bk_end_time: '2020-08-27 10:16:10',
                    bk_time_consunm: '3min',
                    status_choices: 'SUCCESS'
                },
                {
                    ID: '1200',
                    job_object_choices: '进程',
                    job_action_choices: '停止',
                    bk_opera_range: '****************',
                    bk_per_account: 'admin',
                    bk_start_time: '2020-07-05 08:10:08',
                    bk_end_time: '2020-08-27 10:10:10',
                    bk_time_consunm: '3min',
                    status_choices: 'FAILED'
                },{
                    ID: '1200',
                    job_object_choices: '配置文件',
                    job_action_choices: '重启',
                    bk_opera_range: '****************',
                    bk_per_account: 'admin',
                    bk_start_time: '2020-07-05 08:08:08',
                    bk_end_time: '2020-08-27 10:11:10',
                    bk_time_consunm: '3min',
                    status_choices: 'RUNNING'
                },{
                    ID: '1200',
                    job_object_choices: '进程',
                    job_action_choices: '配置下发',
                    bk_opera_range: '****************',
                    bk_per_account: 'admin',
                    bk_start_time: '2020-07-05 08:02:08',
                    bk_end_time: '2020-08-27 10:03:10',
                    bk_time_consunm: '3min',
                    status_choices: 'FAILED'
                },{
                    ID: '1200',
                    job_object_choices: '配置文件',
                    job_action_choices: '重载',
                    bk_opera_range: '****************',
                    bk_per_account: 'admin',
                    bk_start_time: '2020-07-05 08:00:08',
                    bk_end_time: '2020-08-27 10:30:10',
                    bk_time_consunm: '3min',
                    status_choices: 'SUCCESS'
                },{
                    ID: '1200',
                    job_object_choices: '进程',
                    job_action_choices: '强制停止',
                    bk_opera_range: '****************',
                    bk_per_account: 'admin',
                    bk_start_time: '2020-07-05 08:12:08',
                    bk_end_time: '2020-08-27 10:36:10',
                    bk_time_consunm: '3min',
                    status_choices: 'FAILED'
                },{
                    ID: '1200',
                    job_object_choices: '配置文件',
                    job_action_choices: '托管',
                    bk_opera_range: '**********************************************************',
                    bk_per_account: 'admin',
                    bk_start_time: '2020-07-05 08:32:08',
                    bk_end_time: '2020-08-27 10:45:10',
                    bk_time_consunm: '3min',
                    status_choices: 'SUCCESS'
                },{
                    ID: '1200',
                    job_object_choices: '进程',
                    job_action_choices: '取消托管',
                    bk_opera_range: '****************',
                    bk_per_account: 'admin',
                    bk_start_time: '2020-07-05 08:45:08',
                    bk_end_time: '2020-08-27 10:12:10',
                    bk_time_consunm: '3min',
                    status_choices: 'RUNNING'
                }
            ],
            message: 'ok'
        }
    }
    if (invoke === 'getTaskHistoryDetail') {
        return {
            code: 0,
            result: true,
            data: {
                task_id: '1102',
                template_name: '商城配置',
                version_id: '102',
                per_account: 'admin',
                start_time: '2020-08-27 10:00:00',
                task_type: '配置文件下发',
                file_name: 'config.ini',
                operat_range: '********************************************',
                per_timeout: '3min',
                end_time: '2020-09-10 10:00:00',
                perpory: [
                    {
                        set_name: '大区',
                        template_name: 'upload',
                        server_instance: '0',
                        process_name: 'update',
                        fun_id: '99',
                        process_instance_id: '1231',
                        timeout: '1min',
                        per_status: 'FAILED',
                        erroeMessage: '请求超时'
                    },
                    {
                        set_name: '大区3',
                        template_name: '模板3',
                        server_instance: '2',
                        process_name: 'update',
                        fun_id: '100',
                        process_instance_id: '3123',
                        timeout: '3min',
                        per_status: 'FAILED',
                        erroeMessage: '失败原因长时间未响应'
                    },
                    {
                        set_name: '大区2',
                        template_name: '模板2',
                        server_instance: '2',
                        process_name: 'update',
                        fun_id: '101',
                        process_instance_id: '2121',
                        timeout: '3min',
                        per_status: 'SUCCESS'
                    },
                    {
                        set_name: '大区1',
                        template_name: '模板1',
                        server_instance: '1',
                        process_name: 'update',
                        fun_id: '102',
                        process_instance_id: '1231',
                        timeout: '3min',
                        per_status: 'RUNNING'
                    }
                ]
            },
            message: 'ok'
        }
    }
    if (invoke === 'getTaskHistoryById') {
        return {
            code: 0,
            result: true,
            data: {
                ID: '1200',
                job_object_choices: '进程',
                job_action_choices: '停止',
                bk_opera_range: '****************',
                bk_per_account: 'admin',
                bk_start_time: '2020-07-05 08:08:08',
                bk_end_time: '2020-08-27 10:10:10',
                bk_time_consunm: '3min',
                status_choices: 'FAILED'
            },
            message: 'ok'
        }
    }
    if (invoke === 'getConfigFileDetail') {
        return {
            code: 0,
            result: true,
            data: {
                bk_template_id: "2234",
                bk_template_name: "商城活动配置",
                bk_file_name: "文件名称",
                bk_abs_path: "/date/asdge/asdge",
                bk_file_user: "bencemo",
                bk_file_group: "root",
                bk_file_per: "755",
                bk_output: "linux",
                code_content: `{
                    "name": "arman",
                    "age": 17,
                    'home': '洛阳',
                    'aaaa': '实时',
                    '顶顶顶': '啧啧啧'
                }`,
                language: "yaml"
            },
            message: 'ok'
        }
    }
    if (invoke === 'getFilterCondition') {
        return {
            code: 0,
            result: true,
            data: [
                {
                    id: "set_name",
                    name: '集群',
                    children: [
                        {
                           name: 'set1',
                           id: 'set1'
                        },
                        {
                            name: 'set2',
                            id: 'set2'
                         }
                    ]
                },
                {
                    id: "template_name",
                    name: '模块',
                    children: [
                        {
                           name: 'module1',
                           id: 'module1'
                        },
                        {
                            name: 'module2',
                            id: 'module2'
                         }
                    ]
                },
                {
                    id: "process_name",
                    name: '进程别名',
                    children: [
                        {
                           name: '托管插件',
                           id: 'MAIN_DELEGATE_PLUGIN' 
                        },
                        {
                            name: '取消托管插件',
                            id: 'MAIN_UNDELEGATE_PLUGIN' 
                         }
                    ]
                },
                {
                    id: "per_status",
                    name: '执行状态',
                    children: [
                        {
                           name: '执行失败',
                           id: 'FAILED' 
                        },
                        {
                            name: '已终止',
                            id: 'TERMINATED' 
                         }
                    ]
                }
            ],
            message: 'ok'
        }
    }
    return {
        code: 1,
        data: null,
        message: 'failed'
    }
}
