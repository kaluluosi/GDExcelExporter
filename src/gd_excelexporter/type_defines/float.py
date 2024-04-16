"""
author:        kaluluosi111 <kaluluosi@gmail.com>
date:          2024-04-16 11:28:21
Copyright © Kaluluosi All rights reserved
"""

from gd_excelexporter.core.type_define import TypeDefine


class Float(TypeDefine):
    def convert(self, raw_value: str, id=None):
        return float(raw_value or 0)
