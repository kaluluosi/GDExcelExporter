"""
author:        kaluluosi111 <kaluluosi@gmail.com>
date:          2024-04-16 11:30:02
Copyright © Kaluluosi All rights reserved
"""

from gd_excelexporter.core.type_define import TypeDefine


class ArrayBool(TypeDefine):
    def _convert(self, raw_value: str, id=None):
        _value = (
            [e.upper() not in ["FALSE", "否"] for e in raw_value.split("|")]
            if raw_value
            else []
        )
        return _value
