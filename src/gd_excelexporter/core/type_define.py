"""
author:        kaluluosi111 <kaluluosi@gmail.com>
date:          2024-04-16 11:14:32
Copyright © Kaluluosi All rights reserved
"""

import abc
import re
import sys
from typing import Any, ClassVar, Set
from pydantic import BaseModel, Field

if sys.version_info < (3, 10):
    from importlib_metadata import entry_points
else:
    from importlib.metadata import entry_points


class TypeDefine(BaseModel, abc.ABC):
    """
    类型定义解析基类
    """

    TYPE_DEFINE_PATTERN: ClassVar[str] = (
        r"(?P<local>#?)(?P<type_name>\w+)(?P<params>\(.*\))?"
    )

    type_txt: str = Field(description="配置表中类型字符串，比如#string array_str这些")
    is_localized: bool
    type_name: str
    params: str

    @classmethod
    def _get_type_info(cls, type_txt: str):
        m = re.match(cls.TYPE_DEFINE_PATTERN, type_txt)
        if m:
            is_localized = m.group("local") == "#"
            type_name = m.group("type_name")
            params = m.group("params") or "(args=[])"

            return is_localized, type_name, params
        raise ValueError(f"{type_txt} 不是有效的类型定义格式")

    @abc.abstractmethod
    def convert(self, raw_value: str, id=None) -> Any: ...

    @staticmethod
    def register_type_defines():
        """
        获取entry point中注册了的TypeDefine
        """
        tds = entry_points(group="gd_excelexporter.type_define")
        return tds

    @classmethod
    def from_str(cls, type_txt: str):
        """
        从类型定义字符串中创建类型定义

        type_txt 就是配置表第一行的类型定义串

        Args:
            type_txt (str): 类型定义串

        Returns:
            TypeDefine: 类型定义
        """
        is_localized, type_name, params = cls._get_type_info(type_txt)
        type_defines = cls.register_type_defines()
        if type_name in type_defines.names:
            type_define_cls = type_defines[type_name].load()
            return type_define_cls(
                type_txt=type_txt, is_localized=is_localized, params=params
            )
        raise ValueError(f"{type_txt} {type_name} 没有适合的类型定义解析器")


class TrTypeDefine(TypeDefine):
    """
    多语言抽取用
    """

    # 用于多语言抽取
    __tr_strs__: ClassVar[Set[str]] = set()
