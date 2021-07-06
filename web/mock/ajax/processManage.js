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
    if (invoke === 'processList') {
        return {
            code: 0,
            result: true,
            data: {
                total: 1000,
                list: [
                    {
                        bk_inner_id: '127.0.0.1',
                        bk_set_name: 'QQ',
                        bk_module_name: '吉祥',
                        bk_service_name: '美丽',
                        bk_process_name: '周一闻',
                        bk_process_id: 6666,
                        instance_id: 66666666,
                        process_status: 'fail',
                        delegate_status: 'delegated',
                        bk_cloud_name: 'loihjkgfh',
                        config_template_count: 1,
                        config_file: {
                            '1': '102 mysql （mysql.ini)',
                            '2': '103 mysql2 （mysql_safe.ini'
                        }
                    },
                    {
                        bk_inner_id: '127.0.0.1',
                        bk_set_name: '微信',
                        bk_module_name: '幸福',
                        bk_service_name: '开心',
                        bk_process_name: '周二闻',
                        bk_process_id: 77777,
                        instance_id: 777777777,
                        process_status: 'success',
                        delegate_status: 'delegated',
                        bk_cloud_name: 'gdrter',
                        config_template_count: 2,
                        config_file: {
                            '1': '102 mysql （mysql.ini)',
                            '2': '103 mysql2 （mysql_safe.ini'
                        }
                    },
                    {
                        bk_inner_id: '127.0.0.1',
                        bk_set_name: '支付宝',
                        bk_module_name: '富贵',
                        bk_service_name: '发财',
                        bk_process_name: '周三闻',
                        bk_process_id: 88888,
                        instance_id: 88888,
                        process_status: '',
                        delegate_status: '',
                        bk_cloud_name: 'adsadserwer',
                        config_template_count: 0,
                        config_file: {
                            '1': '102 mysql （mysql.ini)',
                            '2': '103 mysql2 （mysql_safe.ini'
                        }
                    }
                ]
            },
            message: 'ok'
        }
    }
    if (invoke === 'searchList') {
        return {
            code: 0,
            result: true,
            data: {
                total: 1000,
                list: {
                    setName: [
                        {
                            id: 'test',
                            name: '测试',
                            isSelected: false,
                            children: [
                                {
                                    id: 1,
                                    name: '测试',
                                    isSelected: false
                                }, {
                                    id: 2,
                                    name: '测试1',
                                    isSelected: false
                                }, {
                                    id: 3,
                                    name: '测试2',
                                    isSelected: false
                                }, {
                                    id: 4,
                                    name: '测试3',
                                    isSelected: false
                                }
                            ]
                        }, {
                            id: 'experience',
                            name: '体验',
                            isSelected: false,
                            children: [
                                {
                                    id: 5,
                                    name: '体验',
                                    isSelected: false
                                }, {
                                    id: 6,
                                    name: '体验1',
                                    isSelected: false
                                }, {
                                    id: 7,
                                    name: '体验2',
                                    isSelected: false
                                }, {
                                    id: 8,
                                    name: '体验3',
                                    isSelected: false
                                }
                            ]
                        }, {
                            id: 'formal',
                            name: '正式',
                            isSelected: false,
                            children: [
                                {
                                    id: 9,
                                    name: '正式',
                                    isSelected: false
                                }, {
                                    id: 10,
                                    name: '正式1',
                                    isSelected: false
                                }, {
                                    id: 11,
                                    name: '正式2',
                                    isSelected: false
                                }, {
                                    id: 12,
                                    name: '正式3',
                                    isSelected: false
                                }, 
                            ]
                        }
                    ],
                    module: [
                        { id: 3, name: '打球' },
                        { id: 4, name: '跳舞' }
                    ],
                    serviceInstance: [
                        { id: 5, name: '健身' },
                        { id: 6, name: '骑车' }
                    ],
                    processName: [
                        { id: 7, name: 'k8s' },
                        { id: 8, name: 'K8S' }
                    ],
                    instanceId: [
                        { id: 9, name: 'mesos' },
                        { id: 10, name: 'MESOS' }
                    ]
                }
            },
            message: 'ok'
        }
    }
    if (invoke === 'topologyList') {
        return {
            code: 0,
            result: true,
            data:[
                {
                    "bk_inst_id": 1,
                    "bk_inst_name": "蓝鲸",
                    "bk_obj_id": "biz",
                    "child": [
                        {
                            "bk_inst_id": 11,
                            "bk_inst_name": "鲸",
                            "bk_obj_id": "set",
                            "child": [
                                {
                                    "bk_inst_id": 12,
                                    "bk_inst_name": "jobqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq",
                                    "bk_obj_id": "module",
                                    "child": [
                                        {
                                            "bk_inst_id": 43,
                                            "bk_inst_name": "job2",
                                            "status": true,
                                            "bk_obj_id": "module",
                                            "child": [],
                                            "service_template_id": 123
                                        }
                                    ],
                                    "service_template_id": 0
                                },
                                {
                                    "bk_inst_id": 13,
                                    "bk_inst_name": "job2",
                                    "status": true,
                                    "bk_obj_id": "module",
                                    "child": [],
                                    "service_template_id": 123
                                }
                            ]
                        }
                    ]
                },
                {
                    "bk_inst_id": 2,
                    "bk_inst_name": "蓝鲸",
                    "bk_obj_id": "biz",
                    "child": [
                        {
                            "bk_inst_id": 21,
                            "bk_inst_name": "job",
                            "bk_obj_id": "set",
                            "child": [
                                {
                                    "bk_inst_id": 22,
                                    "bk_inst_name": "job",
                                    "bk_obj_id": "module",
                                    "child": [],
                                    "service_template_id": 0
                                },
                                {
                                    "bk_inst_id": 23,
                                    "bk_inst_name": "job2",
                                    "bk_obj_id": "module",
                                    "status": true,
                                    "child": [],
                                    "service_template_id": 123
                                }
                            ]
                        }
                    ]
                }
            ],
            message: 'ok'
        }
    }
    if (invoke === 'serveTemplateList') {
        return {
            code: 0,
            result: true,
            data: [
                {
                    "bk_biz_id": 1,
                    "id": 51,
                    "name": "周一闻",
                    "service_category_id": 1,
                    "creator": "admin",
                    "modifier": "admin",
                    "create_time": "2019-09-18T20:31:34.627+08:00",
                    "last_time": "2019-09-18T20:31:34.627+08:00",
                    "bk_supplier_account": "0"
                  },
                  {
                    "bk_biz_id": 1,
                    "id": 50,
                    "name": "周二闻",
                    "service_category_id": 1,
                    "creator": "admin",
                    "modifier": "admin",
                    "create_time": "2019-09-18T20:31:29.607+08:00",
                    "last_time": "2019-09-18T20:31:29.607+08:00",
                    "bk_supplier_account": "0"
                  }
                ],
            message: 'ok'
        }
    }
    if (invoke === 'processTemplate') {
        return {
            code: 0,
            result: true,
            data: [
                {
                    "id": 50,
                    "bk_process_name": "p1",
                    "bk_biz_id": 1,
                    "service_template_id": 51,
                    "config_templates": [],
                    "property": {
                        "bk_func_id": "asdad",
                        "protocol": "1",
                        "create_time": "2adadd",
                        "bind_ip": 'asdad',
                        "proc_num": 'zxczcx',
                        "port": "9000",
                        "last_time": "2adadasd",
                        "priority": 'czczc',
                        "pid_file": "",
                        "auto_time_gap": 'asdad',
                        "stop_cmd": "34243",
                        "description": "2424234",
                        "bk_process_id": '89',
                        "bk_process_name": "asdadad",
                        "bk_start_param_regex": "adsadsd",
                        "start_cmd": "asdad",
                        "user": "adasda",
                        "face_stop_cmd": "243424",
                        "bk_biz_id": 7,
                        "bk_func_name": "adsadasd",
                        "work_path": "23244",
                        "timeout": 'adad',
                        "reload_cmd": "dsd",
                        "auto_start": 'adadas',
                        "bk_supplier_account": "0",
                        "bk_enable_port": 'adasdasd',
                        "restart_cmd": "adsad"
                    },
                    "creator": "admin",
                    "modifier": "admin",
                    "create_time": "2019-06-19T15:24:04.763+08:00",
                    "last_time": "2019-06-19T15:24:04.763+08:00",
                    "bk_supplier_account": "0"
                },
                {
                    "id": 211,
                    "bk_process_name": "qwe",
                    "bk_biz_id": 1,
                    "service_template_id": 51,
                    "config_templates": [
                        {
                            "id": 102,
                            "template_name": "mysql.ini",
                            "template_alis": "mysql"
                        },
                        {
                            "id": 103,
                            "template_name": "mysql_safe.ini",
                            "template_alis": "mysql_2"
                        }
                    ],
                    "property": {
                        "bk_func_id": "00",
                        "protocol": "1",
                        "create_time": "00",
                        "bind_ip": 'asdad',
                        "proc_num": '00',
                        "port": "9000",
                        "last_time": "00",
                        "priority": '000',
                        "pid_file": "",
                        "auto_time_gap": '00',
                        "stop_cmd": "0",
                        "description": "0",
                        "bk_process_id": '660',
                        "bk_process_name": "0",
                        "bk_start_param_regex": "0",
                        "start_cmd": "0",
                        "user": "adasda",
                        "face_stop_cmd": "0",
                        "bk_biz_id": 7,
                        "bk_func_name": "0",
                        "work_path": "0",
                        "timeout": '0',
                        "reload_cmd": "0",
                        "auto_start": '0',
                        "bk_supplier_account": "0",
                        "bk_enable_port": '0',
                        "restart_cmd": "0"
                    },
                    "creator": "admin",
                    "modifier": "admin",
                    "create_time": "2019-06-19T15:24:04.763+08:00",
                    "last_time": "2019-06-19T15:24:04.763+08:00",
                    "bk_supplier_account": "0"
                },
                {
                    "id": 32,
                    "bk_process_name": "qewe",
                    "bk_biz_id": 1,
                    "service_template_id": 51,
                    "config_templates": [
                        {
                            "id": 102,
                            "template_name": "mysql.ini",
                            "template_alis": "mysql"
                        },
                        {
                            "id": 103,
                            "template_name": "mysql_safe.ini",
                            "template_alis": "mysql_2"
                        }
                    ],
                    "property": {
                        "bk_func_id": "asdad",
                        "protocol": "1",
                        "create_time": "2adadd",
                        "bind_ip": 'asdad',
                        "proc_num": 'zxczcx',
                        "port": "9000",
                        "last_time": "2adadasd",
                        "priority": 'czczc',
                        "pid_file": "asada",
                        "auto_time_gap": 'asdad',
                        "stop_cmd": "34243",
                        "description": "2424234",
                        "bk_process_id": '54',
                        "bk_process_name": "asdadad",
                        "bk_start_param_regex": "adsadsd",
                        "start_cmd": "asdad",
                        "user": "adasda",
                        "face_stop_cmd": "243424",
                        "bk_biz_id": 7,
                        "bk_func_name": "adsadasd",
                        "work_path": "23244",
                        "timeout": 'adad',
                        "reload_cmd": "dsd",
                        "auto_start": 'adadas',
                        "bk_supplier_account": "0",
                        "bk_enable_port": 'adasdasd',
                        "restart_cmd": "adsad"
                    },
                    "creator": "admin",
                    "modifier": "admin",
                    "create_time": "2019-06-19T15:24:04.763+08:00",
                    "last_time": "2019-06-19T15:24:04.763+08:00",
                    "bk_supplier_account": "0"
                },
                {
                    "id": 12321,
                    "bk_process_name": "sdfsf",
                    "bk_biz_id": 1,
                    "service_template_id": 51,
                    "config_templates": [
                        {
                            "id": 102,
                            "template_name": "mysql.ini",
                            "template_alis": "mysql"
                        },
                        {
                            "id": 103,
                            "template_name": "mysql_safe.ini",
                            "template_alis": "mysql_2"
                        }
                    ],
                    "property": {
                        "bk_func_id": "asdad",
                        "protocol": "1",
                        "create_time": "2adadd",
                        "bind_ip": 'asdad',
                        "proc_num": 'zxczcx',
                        "port": "9000",
                        "last_time": "2adadasd",
                        "priority": 'czczc',
                        "pid_file": "asada",
                        "auto_time_gap": 'asdad',
                        "stop_cmd": "34243",
                        "description": "2424234",
                        "bk_process_id": '464',
                        "bk_process_name": "asdadad",
                        "bk_start_param_regex": "adsadsd",
                        "start_cmd": "asdad",
                        "user": "adasda",
                        "face_stop_cmd": "243424",
                        "bk_biz_id": 7,
                        "bk_func_name": "adsadasd",
                        "work_path": "23244",
                        "timeout": 'adad',
                        "reload_cmd": "dsd",
                        "auto_start": 'adadas',
                        "bk_supplier_account": "0",
                        "bk_enable_port": 'adasdasd',
                        "restart_cmd": "adsad"
                    },
                    "creator": "admin",
                    "modifier": "admin",
                    "create_time": "2019-06-19T15:24:04.763+08:00",
                    "last_time": "2019-06-19T15:24:04.763+08:00",
                    "bk_supplier_account": "0"
                },
                {
                    "id": 213,
                    "bk_process_name": "sdfsd",
                    "bk_biz_id": 1,
                    "service_template_id": 51,
                    "config_templates": [
                        {
                            "id": 102,
                            "template_name": "mysql.ini",
                            "template_alis": "mysql"
                        },
                        {
                            "id": 103,
                            "template_name": "mysql_safe.ini",
                            "template_alis": "mysql_2"
                        }
                    ],
                    "property": {
                        "bk_func_id": "asdad",
                        "protocol": "1",
                        "create_time": "2adadd",
                        "bind_ip": 'asdad',
                        "proc_num": 'zxczcx',
                        "port": "9000",
                        "last_time": "2adadasd",
                        "priority": 'czczc',
                        "pid_file": "asada",
                        "auto_time_gap": 'asdad',
                        "stop_cmd": "34243",
                        "description": "2424234",
                        "bk_process_id": '32',
                        "bk_process_name": "asdadad",
                        "bk_start_param_regex": "adsadsd",
                        "start_cmd": "asdad",
                        "user": "adasda",
                        "face_stop_cmd": "243424",
                        "bk_biz_id": 7,
                        "bk_func_name": "adsadasd",
                        "work_path": "23244",
                        "timeout": 'adad',
                        "reload_cmd": "dsd",
                        "auto_start": 'adadas',
                        "bk_supplier_account": "0",
                        "bk_enable_port": 'adasdasd',
                        "restart_cmd": "adsad"
                    },
                    "creator": "admin",
                    "modifier": "admin",
                    "create_time": "2019-06-19T15:24:04.763+08:00",
                    "last_time": "2019-06-19T15:24:04.763+08:00",
                    "bk_supplier_account": "0"
                },
                {
                    "id": 213321,
                    "bk_process_name": "sdfsf",
                    "bk_biz_id": 1,
                    "service_template_id": 51,
                    "config_templates": [
                        {
                            "id": 102,
                            "template_name": "mysql.ini",
                            "template_alis": "mysql"
                        },
                        {
                            "id": 103,
                            "template_name": "mysql_safe.ini",
                            "template_alis": "mysql_2"
                        }
                    ],
                    "property": {
                        "bk_func_id": "asdad",
                        "protocol": "1",
                        "create_time": "2adadd",
                        "bind_ip": 'asdad',
                        "proc_num": 'zxczcx',
                        "port": "9000",
                        "last_time": "2adadasd",
                        "priority": 'czczc',
                        "pid_file": "asada",
                        "auto_time_gap": 'asdad',
                        "stop_cmd": "34243",
                        "description": "2424234",
                        "bk_process_id": '2',
                        "bk_process_name": "asdadad",
                        "bk_start_param_regex": "adsadsd",
                        "start_cmd": "asdad",
                        "user": "adasda",
                        "face_stop_cmd": "243424",
                        "bk_biz_id": 7,
                        "bk_func_name": "adsadasd",
                        "work_path": "23244",
                        "timeout": 'adad',
                        "reload_cmd": "dsd",
                        "auto_start": 'adadas',
                        "bk_supplier_account": "0",
                        "bk_enable_port": 'adasdasd',
                        "restart_cmd": "adsad"
                    },
                    "creator": "admin",
                    "modifier": "admin",
                    "create_time": "2019-06-19T15:24:04.763+08:00",
                    "last_time": "2019-06-19T15:24:04.763+08:00",
                    "bk_supplier_account": "0"
                },
                {
                    "id": 434,
                    "bk_process_name": "sdfsf",
                    "bk_biz_id": 1,
                    "service_template_id": 51,
                    "config_templates": [
                        {
                            "id": 102,
                            "template_name": "mysql.ini",
                            "template_alis": "mysql"
                        },
                        {
                            "id": 103,
                            "template_name": "mysql_safe.ini",
                            "template_alis": "mysql_2"
                        }
                    ],
                    "property": {
                        "bk_func_id": "asdad",
                        "protocol": "1",
                        "create_time": "2adadd",
                        "bind_ip": 'asdad',
                        "proc_num": 'zxczcx',
                        "port": "9000",
                        "last_time": "2adadasd",
                        "priority": 'czczc',
                        "pid_file": "asada",
                        "auto_time_gap": 'asdad',
                        "stop_cmd": "34243",
                        "description": "2424234",
                        "bk_process_id": '1',
                        "bk_process_name": "asdadad",
                        "bk_start_param_regex": "adsadsd",
                        "start_cmd": "asdad",
                        "user": "adasda",
                        "face_stop_cmd": "243424",
                        "bk_biz_id": 7,
                        "bk_func_name": "adsadasd",
                        "work_path": "23244",
                        "timeout": 'adad',
                        "reload_cmd": "dsd",
                        "auto_start": 'adadas',
                        "bk_supplier_account": "0",
                        "bk_enable_port": 'adasdasd',
                        "restart_cmd": "adsad"
                    },
                    "creator": "admin",
                    "modifier": "admin",
                    "create_time": "2019-06-19T15:24:04.763+08:00",
                    "last_time": "2019-06-19T15:24:04.763+08:00",
                    "bk_supplier_account": "0"
                },
                {
                    "id": 345,
                    "bk_process_name": "sdfsdf",
                    "bk_biz_id": 1,
                    "service_template_id": 51,
                    "config_templates": [
                        {
                            "id": 102,
                            "template_name": "mysql.ini",
                            "template_alis": "mysql"
                        },
                        {
                            "id": 103,
                            "template_name": "mysql_safe.ini",
                            "template_alis": "mysql_2"
                        }
                    ],
                    "property": {
                        "bk_func_id": "asdad",
                        "protocol": "1",
                        "create_time": "2adadd",
                        "bind_ip": 'asdad',
                        "proc_num": 'zxczcx',
                        "port": "9000",
                        "last_time": "2adadasd",
                        "priority": 'czczc',
                        "pid_file": "",
                        "auto_time_gap": 'asdad',
                        "stop_cmd": "34243",
                        "description": "2424234",
                        "bk_process_id": '0',
                        "bk_process_name": "asdadad",
                        "bk_start_param_regex": "adsadsd",
                        "start_cmd": "asdad",
                        "user": "adasda",
                        "face_stop_cmd": "243424",
                        "bk_biz_id": 7,
                        "bk_func_name": "adsadasd",
                        "work_path": "23244",
                        "timeout": 'adad',
                        "reload_cmd": "dsd",
                        "auto_start": 'adadas',
                        "bk_supplier_account": "0",
                        "bk_enable_port": 'adasdasd',
                        "restart_cmd": "adsad"
                    },
                    "creator": "admin",
                    "modifier": "admin",
                    "create_time": "2019-06-19T15:24:04.763+08:00",
                    "last_time": "2019-06-19T15:24:04.763+08:00",
                    "bk_supplier_account": "0"
                }
                
            ],
            message: 'ok'
        }
    }
    if (invoke === 'processInstance') {
        return {
            code: 0,
            result: true,
            data: [
                {
                    "config_templates": [
                        {
                          "id": 0,
                          "template_name": "mysql.ini",
                          "template_alis": "mysql"
                        },
                        {
                          "id": 3,
                          "template_name": "mysql_safe.ini",
                          "template_alis": "mysql_2"
                        }
                    ],
                    "property": {
                        "bk_func_id": "",
                        "protocol": "1",
                        "create_time": "2020-04-11T21:03:53.156+08:00",
                        "bind_ip": null,
                        "proc_num": null,
                        "port": "9000",
                        "last_time": "2020-04-11T21:03:53.393+08:00",
                        "priority": null,
                        "pid_file": "",
                        "auto_time_gap": null,
                        "stop_cmd": "",
                        "description": "",
                        "bk_process_id": 1189,
                        "bk_process_name": "cmdb_adminserver",
                        "bk_start_param_regex": "",
                        "start_cmd": "",
                        "user": "",
                        "face_stop_cmd": "",
                        "bk_biz_id": 7,
                        "bk_func_name": "cmdb_adminserver",
                        "work_path": "",
                        "timeout": null,
                        "reload_cmd": "",
                        "auto_start": null,
                        "bk_supplier_account": "0",
                        "bk_enable_port": true,
                        "restart_cmd": ""
                    },
                    "relation": {
                        "bk_biz_id": 7,
                        "process_template_id": 196,
                        "bk_host_id": 832,
                        "service_instance_id": 1670,
                        "bk_process_id": 1189,
                        "bk_supplier_account": "0"
                    }
                },
                {
                    "config_templates": [
                        {
                          "id": 103,
                          "template_name": "mysql_safe.ini",
                          "template_alis": "mysql_2"
                        },
                        {
                          "id": 102,
                          "template_name": "mysql.ini",
                          "template_alis": "mysql"
                        }
                    ],
                    "property": {
                        "bk_func_id": "213",
                        "protocol": "打算",
                        "create_time": "2020-04-11T21:03:53.156+08:00",
                        "bind_ip": '阿达',
                        "proc_num": '二闻',
                        "port": "9000",
                        "last_time": "2020-04-11T21:03:53.393+08:00",
                        "priority": 'fd',
                        "pid_file": "士大夫",
                        "auto_time_gap": 'dfgdg',
                        "stop_cmd": "士大夫",
                        "description": "撒旦飞洒",
                        "bk_process_id": 21212,
                        "bk_process_name": "cmdb_admin",
                        "bk_start_param_regex": "fgdg",
                        "start_cmd": "阿斯蒂芬",
                        "user": "撒地方",
                        "face_stop_cmd": "撒旦飞洒",
                        "bk_biz_id": 7,
                        "bk_func_name": "'啊飒飒",
                        "work_path": "dfgd",
                        "timeout": '123',
                        "reload_cmd": "dfgdg",
                        "auto_start": '阿萨',
                        "bk_supplier_account": "0",
                        "bk_enable_port": true,
                        "restart_cmd": "dfgdg"
                    },
                    "relation": {
                        "bk_biz_id": 7,
                        "process_template_id": 196,
                        "bk_host_id": 832,
                        "service_instance_id": 1670,
                        "bk_process_id": 1189,
                        "bk_supplier_account": "0"
                    }
                }
            ],
            message: 'ok'
        }
    }
    if (invoke === 'updateInstance') {
        return {
            code: 0,
            result: true,
            data: [],
            message: 'ok'
        }
    }
    if (invoke === 'updateTemplate') {
        return {
            code: 0,
            result: true,
            data: {
                "job_id": 1
            },
            message: 'ok'
        }
    }
    if (invoke === 'getTemplateList') {
        return {
            code: 0,
            result: true,
            data: [
                {
                    "id": 1,
                    "template_name": "活动配置",
                    "file_name": "config.ini",
                    "abs_path": "/data/lol/pro/",
                    "owner": "root",
                    "group": "root",
                    "filemode": "644",
                    "format": "yaml",
                    "created_by": "admin",
                    "creat_time": '2020-09-21 12:34:56'
                },
                {
                    "id": 2,
                    "template_name": "fsfsd",
                    "file_name": "sdfsf",
                    "abs_path": "/data/lol/pro/",
                    "owner": "root",
                    "group": "root",
                    "filemode": "644",
                    "format": "yaml",
                    "created_by": "admin",
                    "creat_time": '2020-07-21 12:34:56'
                },
                {
                    "id": 3,
                    "template_name": "sfsdf",
                    "file_name": "ghgfh",
                    "abs_path": "/data/lol/pro/",
                    "owner": "root",
                    "group": "root",
                    "filemode": "644",
                    "format": "yaml",
                    "created_by": "admin",
                    "creat_time": '2020-09-21 12:34:56'
                },
                {
                    "id": 4,
                    "template_name": "ghjgj",
                    "file_name": "khjkk",
                    "abs_path": "/data/lol/pro/",
                    "owner": "root",
                    "group": "root",
                    "filemode": "644",
                    "format": "yaml",
                    "created_by": "admin",
                    "creat_time": '2020-09-21 12:34:56'
                },
                {
                    "id": 5,
                    "template_name": "hikyu",
                    "file_name": "bmbm",
                    "abs_path": "/data/lol/pro/",
                    "owner": "root",
                    "group": "root",
                    "filemode": "644",
                    "format": "yaml",
                    "created_by": "admin",
                    "creat_time": '2020-09-21 12:34:56'
                },
                {
                    "id": 6,
                    "template_name": "zxcvxz",
                    "file_name": "dfreg",
                    "abs_path": "/data/lol/pro/",
                    "owner": "root",
                    "group": "root",
                    "filemode": "644",
                    "format": "yaml",
                    "created_by": "admin",
                    "creat_time": '2020-09-21 12:34:56'
                },
                {
                    "id": 7,
                    "template_name": "765ujh",
                    "file_name": "324wer",
                    "abs_path": "/data/lol/pro/",
                    "owner": "root",
                    "group": "root",
                    "filemode": "644",
                    "format": "yaml",
                    "created_by": "admin",
                    "creat_time": '2020-09-21 12:34:56'
                },
                {
                    "id": 8,
                    "template_name": "nvhbj76",
                    "file_name": "yd5",
                    "abs_path": "/data/lol/pro/",
                    "owner": "root",
                    "group": "root",
                    "filemode": "644",
                    "format": "yaml",
                    "created_by": "admin",
                    "creat_time": '2020-09-21 12:34:56'
                }
            ],
            message: 'ok'
        }
    }
    if (invoke === 'getConfigInfo') {
        return {
            code: 0,
            result: true,
            data: {
                id: 1,
                template_name: '活动配置',
                file_name: 'config.ini',
                path: '/data/',
                update_person: 'arman',
                last_time: '2020-09-09 12:34:25',
                update_time: '2020-09-15 12:35:25',
                code_content: `{
                    "name": "arman",
                    "age": 17,
                    'home': '洛阳',
                    'aaaa': '实时',
                    '顶顶顶': '啧啧啧'
                }`,
                last_version: `{
                    "name": "arman",
                    "age": 30,
                    "a": {
                    },
                    "c": [1, 2, 3],
                    "d": [ ],
                    'home': '洛阳',
                    'aaaa': '实时',
                    '啦啦啦': '烦烦烦'
                }`,
                format: "yaml",
            },
            message: 'ok'
        }
    }
    if (invoke === 'setReleaseConfig') {
        return {
            code: 0,
            result: true,
            data: [],
            message: 'ok'
        }
    }
    if (invoke === 'setGenerateConfig') {
        return {
            code: 0,
            result: true,
            data: [],
            message: 'ok'
        }
    }
    if (invoke === 'getConfigFileList') {
        return {
            code: 0,
            result: true,
            data: [
                {
                    bk_module_name: '拉拉',
                    bk_file_name: '撒大大',
                    bk_set_name: '是的',
                    bk_process_name: '放松得',
                    bk_process_id: '22',
                    instance_id: '43',
                    bk_inner_id: '76',
                    process_status: 'generated',
                    time: '2020-09-23 10:10:10'
                },
                {
                    bk_module_name: '拉拉',
                    bk_file_name: '撒大大',
                    bk_set_name: '是的',
                    bk_process_name: '放松得',
                    bk_process_id: '22',
                    instance_id: '43',
                    bk_inner_id: '76',
                    process_status: 'generated',
                    time: '2020-09-23 10:10:10'
                },
                {
                    bk_module_name: '拉拉',
                    bk_file_name: '撒大大',
                    bk_set_name: '是的',
                    bk_process_name: '放松得',
                    bk_process_id: '22',
                    instance_id: '43',
                    bk_inner_id: '76',
                    process_status: '',
                    time: '2020-09-23 10:10:10'
                },{
                    bk_module_name: '拉拉',
                    bk_file_name: '撒大大',
                    bk_set_name: '是的',
                    bk_process_name: '放松得',
                    bk_process_id: '22',
                    instance_id: '43',
                    bk_inner_id: '76',
                    process_status: 'generated',
                    time: '2020-09-23 10:10:10'
                },{
                    bk_module_name: '拉拉',
                    bk_file_name: '撒大大',
                    bk_set_name: '是的',
                    bk_process_name: '放松得',
                    bk_process_id: '22',
                    instance_id: '43',
                    bk_inner_id: '76',
                    process_status: '',
                    time: '2020-09-23 10:10:10'
                },{
                    bk_module_name: '拉拉',
                    bk_file_name: '撒大大',
                    bk_set_name: '是的',
                    bk_process_name: '放松得',
                    bk_process_id: '22',
                    instance_id: '43',
                    bk_inner_id: '76',
                    process_status: 'generated',
                    time: '2020-09-23 10:10:10'
                },{
                    bk_module_name: '拉拉',
                    bk_file_name: '撒大大',
                    bk_set_name: '是的',
                    bk_process_name: '放松得',
                    bk_process_id: '22',
                    instance_id: '43',
                    bk_inner_id: '76',
                    process_status: '',
                    time: '2020-09-23 10:10:10'
                },{
                    bk_module_name: '拉拉',
                    bk_file_name: '撒大大',
                    bk_set_name: '是的',
                    bk_process_name: '放松得',
                    bk_process_id: '22',
                    instance_id: '43',
                    bk_inner_id: '76',
                    process_status: 'generated',
                    time: '2020-09-23 10:10:10'
                },{
                    bk_module_name: '拉拉',
                    bk_file_name: '撒大大',
                    bk_set_name: '是的',
                    bk_process_name: '放松得',
                    bk_process_id: '22',
                    instance_id: '43',
                    bk_inner_id: '76',
                    process_status: '',
                    time: '2020-09-23 10:10:10'
                },{
                    bk_module_name: '拉拉',
                    bk_file_name: '撒大大',
                    bk_set_name: '是的',
                    bk_process_name: '放松得',
                    bk_process_id: '22',
                    instance_id: '43',
                    bk_inner_id: '76',
                    process_status: 'generated',
                    time: '2020-09-23 10:10:10'
                }
            ],
            message: 'ok'
        }
    }
    if (invoke === 'getFilterCondition') {
        return {
            code: 0,
            result: true,
            data: [
                {
                    id: "bk_host_innerip",
                    name: '内外IP',
                    children: [
                        {
                           name: 'lala',
                           id: 'lala' 
                        },
                        {
                            name: 'xiix',
                            id: 'xiix' 
                         }
                    ]
                },
                {
                    id: "process_status",
                    name: '进程状态',
                    children: [
                        {
                            name: '未注册',
                            id: '0'
                        },
                        {
                            name: '运行中',
                            id: '1'
                        },
                        {
                            name: '已终止',
                            id: '2'
                        }
                    ]
                },
                {
                    id: "is_auto",
                    name: '托管状态',
                    children: [
                        {
                            name: '托管',
                            id: 'true'
                        },
                        {
                            name: '未托管',
                            value: 'false'
                        }
                    ]
                },
                {
                    id: "bk_cloud_name",
                    name: '云区域',
                    children: [
                        {
                           name: 'cloud1',
                           id: 'cloud1'
                        },
                        {
                            name: 'cloud2',
                            id: 'cloud2'
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


