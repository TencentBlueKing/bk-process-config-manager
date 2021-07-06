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
from concurrent.futures import as_completed
from concurrent.futures.thread import ThreadPoolExecutor
from multiprocessing.pool import ThreadPool

from django.conf import settings

from apps.exceptions import AppBaseException
from apps.utils.local import get_request


def batch_request(
    func, params, get_data=lambda x: x["info"], get_count=lambda x: x["count"], limit=500,
):
    """
    异步并发请求接口
    :param func: 请求方法
    :param params: 请求参数
    :param get_data: 获取数据函数
    :param get_count: 获取总数函数
    :param limit: 一次请求数量
    :return: 请求结果
    """

    # 如果该接口没有返回count参数，只能同步请求
    if not get_count:
        return sync_batch_request(func, params, get_data, limit)

    # 请求第一次获取总数
    first_params = dict(page={"start": 0, "limit": limit, "return_total": True}, **params)
    result = func(first_params)
    count = int(get_count(result))
    data = get_data(result)
    start = limit

    # 根据请求总数并发请求
    pool = ThreadPool(20)
    futures = []
    try:
        params["_request"] = get_request()
    except AppBaseException:
        # celery下 无request对象
        pass

    while start < count:
        request_params = dict(page={"limit": limit, "start": start}, **params)
        futures.append(pool.apply_async(func, args=(request_params,)))

        start += limit

    pool.close()
    pool.join()

    # 取值
    for future in futures:
        data.extend(get_data(future.get()))

    return data


def sync_batch_request(func, params, get_data=lambda x: x["info"], limit=500):
    """
    同步请求接口
    :param func: 请求方法
    :param params: 请求参数
    :param get_data: 获取数据函数
    :param limit: 一次请求数量
    :return: 请求结果
    """
    # 如果该接口没有返回count参数，只能同步请求
    # 合理的方式应该敦促接口放提供count返回值使用异步请求
    data = []
    start = 0

    # 根据请求总数并发请求
    while True:
        request_params = {"page": {"limit": limit, "start": start}}
        request_params.update(params)
        result = get_data(func(request_params))
        data.extend(result)
        if len(result) < limit:
            break
        else:
            start += limit

    return data


def request_multi_thread(
    func,
    params_list,
    get_data=lambda x: x.get("info", []) if x else [],
    get_request_target=lambda x: x.get("params", {}),
):
    """
    并发请求接口，每次按不同参数请求最后叠加请求结果
    :param func: 请求方法
    :param params_list: 参数列表
    :param get_data: 获取数据函数
    :param get_request_target:
    :return: 请求结果累计
    """
    # 参数预处理，添加request_id
    try:
        _request = get_request()
    except AppBaseException:
        # celery下 无request对象
        pass
    else:
        for params in params_list:
            get_request_target(params)["_request"] = _request

    result = []
    with ThreadPoolExecutor(max_workers=settings.CONCURRENT_NUMBER) as ex:
        tasks = [ex.submit(func, **params) for params in params_list]
    for future in as_completed(tasks):
        result.extend(get_data(future.result()))
    return result
