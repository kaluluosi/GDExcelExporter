"""
author:        kaluluosi111 <kaluluosi@gmail.com>
date:          2024-04-16 11:24:21
Copyright © Kaluluosi All rights reserved
"""

from gd_excelexporter.core.type_define import TypeDefine


class String(TypeDefine):
    def _convert(self, raw_value: str, id=None):
        _value = str(raw_value) if raw_value else ""
        return _value
