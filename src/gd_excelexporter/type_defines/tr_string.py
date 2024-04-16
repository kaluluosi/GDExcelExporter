"""
author:        kaluluosi111 <kaluluosi@gmail.com>
date:          2024-04-16 12:08:49
description:   tr_string 是本地化字符类型，会被抽取到POT
Copyright © Kaluluosi All rights reserved
"""

from gd_excelexporter.core.type_define import TrTypeDefine


class TrString(TrTypeDefine):
    def convert(self, raw_value: str, id=None):
        _value = str(raw_value) if raw_value else ""
        self.__tr_strs__.add(_value)
        return _value
