"""
author:        kaluluosi111 <kaluluosi@gmail.com>
date:          2024-04-16 11:29:39
Copyright © Kaluluosi All rights reserved
"""

from gd_excelexporter.core.type_define import TypeDefine


class ArrayStr(TypeDefine):
    def convert(self, raw_value: str, id=None):
        _value = ["%s" % e for e in raw_value.split("|")] if raw_value else []
        return _value
