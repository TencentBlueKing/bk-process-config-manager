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

from django.utils.translation import ugettext as _
from mako.exceptions import MakoException, RichTraceback
from mako.template import Template

from apps.gsekit.configfile.exceptions import ConfigVersionRenderException
from apps.utils.mako_utils.checker import clean_mako_content
from apps.utils.mako_utils.context import MakoSandbox
from common.log import logger

TEMPLATE_CACHE = {}


def get_cache_template(content: str) -> Template:
    content = clean_mako_content(content)

    # 缓存template，避免重复构造耗时
    template = TEMPLATE_CACHE.get(content)
    if not template:
        template = Template(content)
        TEMPLATE_CACHE[content] = template
    return template


def mako_render(content, context):
    template = get_cache_template(content)
    try:
        with MakoSandbox():
            return template.render(**context)
    except MakoException as error:
        logger.exception(error)
        raise ConfigVersionRenderException(error_message=error)
    except Exception as error:
        logger.exception(error)
        traceback = RichTraceback()
        error_message = traceback.message
        for _traceback in traceback.traceback:
            __, lineno, function, line = _traceback
            if function == "render_body":
                error_message = _("第{lineno}行：{line}，错误：{message}").format(
                    lineno=lineno, line=line, message=traceback.message
                )
        raise ConfigVersionRenderException(error_message=error_message)
