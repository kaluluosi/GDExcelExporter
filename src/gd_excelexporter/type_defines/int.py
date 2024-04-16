"""
author:        kaluluosi111 <kaluluosi@gmail.com>
date:          2024-04-16 11:23:02
Copyright © Kaluluosi All rights reserved
"""

from gd_excelexporter.core.type_define import TypeDefine


class Int(TypeDefine):
    def convert(self, raw_value: str, id=None):
        return int(float(raw_value or 0))
