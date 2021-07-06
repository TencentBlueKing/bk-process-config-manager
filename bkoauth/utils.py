# -*- coding: utf-8 -*-
import re

UIN_PATTERN = re.compile(r"^o(?P<uin>\d{3,32})$")


def transform_uin(uin):
    """
    将腾讯云的uin转换为字符型的qq号
    就是去掉第一个字符然后转为整形
    o0836324475 -> 836324475
    o2459422247 -> 2459422247
    """
    match = UIN_PATTERN.match(uin)
    if match:
        uin = str(int(match.groupdict()["uin"]))
    return uin


class FancyDict(dict):
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError as k:
            raise AttributeError(k)

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        try:
            del self[key]
        except KeyError as k:
            raise AttributeError(k)


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for
    else:
        ip = request.META["REMOTE_ADDR"]
    return ip
