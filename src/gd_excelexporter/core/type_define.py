"""
author:        kaluluosi111 <kaluluosi@gmail.com>
date:          2024-04-16 11:14:32
Copyright © Kaluluosi All rights reserved
"""

import abc
from typing import ClassVar, Set
from pydantic import BaseModel, Field


class TypeDefine(BaseModel, abc.ABC):
    """
    类型定义基类
    """

    TYPE_DEFINE_PATTERN: ClassVar[str] = (
        r"(?P<local>#?)(?P<type_name>\w+)(?P<params>\(.*\))?"
    )

    type_txt: str = Field(description="配置表中类型字符串，比如#string array_str这些")

    @abc.abstractmethod
    def convert(self, raw_value: str, id=None): ...

    @classmethod
    def from_str(cls, type_txt: str):
        pass


class TrTypeDefine(TypeDefine):
    """
    多语言抽取用
    """

    # 用于多语言抽取
    __tr_strs__: ClassVar[Set[str]] = set()
