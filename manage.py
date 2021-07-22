#!/usr/bin/env python
import os
import sys

from apps.utils.mako_utils.patch import default_black_list, patch

# 把本地import的优先级设为最低
cur_dir = os.path.dirname(os.path.abspath(__file__))
while cur_dir in sys.path:
    sys.path.remove(cur_dir)
sys.path.append(cur_dir)

if __name__ == "__main__":

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

    from django.core.management import execute_from_command_line

    patch(default_black_list)
    execute_from_command_line(sys.argv)
