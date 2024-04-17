"""
author:        kaluluosi111 <kaluluosi@gmail.com>
date:          2024-04-16 12:09:15
Copyright © Kaluluosi All rights reserved
"""

from gd_excelexporter.core.type_define import TrTypeDefine


class TrDict(TrTypeDefine):
    def _convert(self, raw_value: str, id=None):
        _value = eval(f'{{{raw_value.replace("|",",")}}}') if raw_value else {}
        for k, v in _value.items():
            if isinstance(v, str):
                self.__tr_strs__.add(v)
                _value[k] = v

        return _value
