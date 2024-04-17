"""
author:        kaluluosi111 <kaluluosi@gmail.com>
date:          2024-04-16 11:28:43
Copyright © Kaluluosi All rights reserved
"""

from gd_excelexporter.core.type_define import TypeDefine


class Bool(TypeDefine):
    def _convert(self, raw_value: str, id=None):
        if raw_value:
            if isinstance(raw_value, str):  # 检查 value 是否为字符串
                _value = (
                    raw_value.lower() != "false"
                )  # 如果是字符串，将 value 转换为小写后进行比较
        else:
            _value = False
        return _value
