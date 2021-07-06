#!/usr/bin/env python
import os
import sys

from apps.utils.mako_utils.patch import default_black_list, patch

if __name__ == "__main__":

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

    from django.core.management import execute_from_command_line

    patch(default_black_list)
    execute_from_command_line(sys.argv)
