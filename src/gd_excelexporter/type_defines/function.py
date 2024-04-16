"""
author:        kaluluosi111 <kaluluosi@gmail.com>
date:          2024-04-16 12:07:24
Copyright © Kaluluosi All rights reserved
"""

from gd_excelexporter.core.type_define import TypeDefine


class Function(TypeDefine):
    def convert(self, raw_value: str, id=None):
        if not raw_value:
            return "pass"

        return raw_value
