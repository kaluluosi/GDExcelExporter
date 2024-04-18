"""
author:        kaluluosi111 <kaluluosi@gmail.com>
date:          2024-04-16 12:09:47
Copyright © Kaluluosi All rights reserved
"""

from gd_excelexporter.core.type_define import TrTypeDefine


class TrArrayStr(TrTypeDefine):
    def _convert(self, raw_value: str, id=None):
        _value = ["%s" % e for e in raw_value.split("|")] if raw_value else []

        for v in _value:
            self.__tr_strs__.add(v)

        return _value
