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
import functools
import uuid
from importlib import import_module
from threading import local

from apps.utils.mako_utils.exceptions import ForbiddenMakoTemplateException

in_user_code_thread_ids = []
_local = local()


def set_thread_id(thread_id=None):
    """
    激活thread线程变量
    """
    if not thread_id:
        thread_id = str(uuid.uuid4())
    _local.thread_id = thread_id
    return thread_id


def get_thread_id():
    return getattr(_local, "thread_id", None)


def patch(black_list):
    for module_name, call_names in black_list.items():
        module = import_module(module_name)

        for call_name in call_names:

            def create_patched_call():
                call = getattr(module, call_name)

                @functools.wraps(call)
                def patched_call(*args, **kwargs):
                    thread_id = get_thread_id()
                    if thread_id in in_user_code_thread_ids:
                        raise ForbiddenMakoTemplateException("I am watching you!")
                    else:
                        return call(*args, **kwargs)

                return patched_call

            try:
                new_call = create_patched_call()
            except AttributeError:
                continue

            setattr(module, call_name, new_call)


default_black_list = {
    "os": [
        "system",
        "chdir",
        "chmod",
        "kill",
        "link",
        "listdir",
        "mkdir",
        "putenv",
        "remove",
        "rename",
        "rmdir",
        "scandir",
        "symlink",
        "system",
        "truncate",
        "utime",
        "popen",
        "execl",
        "execle",
        "execv",
        "execlp",
        "execlpe",
        "execvp",
        "execvpe",
        "spawnl",
        "spawnlpe",
        "spawnv",
        "spawnlp",
        "spawnve",
        "getenv",
        "fdopen",
        "spawnvpe",
    ],
    "subprocess": ["Popen", "call", "getstatusoutput", "getoutput", "check_output", "check_call", "run"],
    "ctypes": [
        "addressof",
        "create_string_buffer",
        "create_unicode_buffer",
        "string_at",
        "wstring_at",
        "CDLL",
        "PyDLL",
        "LibraryLoader",
    ],
    "fcntl": ["fcntl", "flock", "ioctl", "lockf"],
    "glob": ["glob"],
    "imaplib": ["socket"],
    "pdb": ["Pdb"],
    "pty": ["spawn"],
    "shutil": [
        "copy",
        "copy2",
        "chown",
        "which",
        "disk_usage",
        "copyfile",
        "copymode",
        "copytree",
        "copystat",
        "copytree",
        "make_archive",
        "move",
        "rmtree",
        "unpack_archive",
    ],
    "signal": [
        "pthread_kill",
        "pause",
        "pthread_sigmask",
        "set_wakeup_fd",
        "setitimer",
        "siginterrupt",
        "sigpending",
        "sigwait",
    ],
    "socket": [
        "socket",
        "create_connection",
        "getaddrinfo",
        "gethostbyaddr",
        "gethostbyname",
        "gethostname",
        "getnameinfo",
        "getservbyname",
        "getservbyport",
        "sethostname",
    ],
    "sys": [
        "callstats",
        "call_tracing",
        "getprofile",
        "setcheckinterval",
        "setdlopenflags",
        "setrecursionlimit",
        "setswitchinterval",
        "setprofile",
        "set_asyncgen_hooks",
        "set_coroutine_origin_tracking_depth",
        "set_coroutine_wrapper",
        "settrace",
        "exit",
        "__loader__",
    ],
    "tempfile": ["mkdtemp", "mkstemp"],
    "webbrowser": ["open"],
}
