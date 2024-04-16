import enum
import logging
import abc

from pydantic import BaseModel, field_validator
from gd_excelexporter.core.models import TypeDefine
from typing import Any, Generic, List, Set, TypeVar, Type


T = TypeVar("T")
logger = logging.getLogger()


# region 类型转换器定义
class Variant(BaseModel, abc.ABC, Generic[T]):
    id: Any
    type_define: TypeDefine
    field_name: str
    value: T

    def local_strs(self) -> Set[str]:
        """
        获取本地化字符串

        因为每个字段的本地化字符串是不同的，所以需要子类重写这个方法

        Returns:
            set[str]: 本地化字符串
        """
        return set()

    @field_validator("value", mode="before")
    @abc.abstractmethod
    @classmethod
    def convert_value(cls, v):
        return ""


class String(Variant[str]):
    def local_strs(self):
        localizeds = set()
        if self.type_define.is_localization:
            localizeds.add(self.value)
        return localizeds

    @field_validator("value", mode="before")
    @classmethod
    def convert_value(cls, v):
        return str(v) if v else ""


class Int(Variant[int]):
    @field_validator("value", mode="before")
    @classmethod
    def convert_value(cls, v):
        return int(float(v or 0))


class Float(Variant[float]):
    @field_validator("value", mode="before")
    @classmethod
    def convert_value(cls, v):
        return int(float(v or 0))


class Bool(Variant[bool]):
    @field_validator("value", mode="before")
    @classmethod
    def convert_value(cls, v):
        if isinstance(v, str):  # 检查 value 是否为字符串
            _value = v.lower() != "false"  # 如果是字符串，将 value 转换为小写后进行比较
        else:
            _value = v is not False  # 如果不是字符串，直接与 False 进行比较
        return _value


class Array(Variant[list]):
    def local_strs(self):
        localizeds = set()
        if self.type_define.is_localization:
            for e in self.value:
                if isinstance(e, str):
                    localizeds.add(e)
        return localizeds

    @field_validator("value", mode="before")
    @classmethod
    def convert_value(cls, v: str):
        _value = eval(f'[{v.replace("|",",")}]') if v else []
        return _value


class ArrayStr(Variant[List[str]]):
    def local_strs(self):
        localizeds = set()
        if self.type_define.is_localization:
            for e in self.value:
                if isinstance(e, str):
                    localizeds.add(e)
        return localizeds

    @field_validator("value", mode="before")
    @classmethod
    def convert_value(cls, v: str):
        _value = ["%s" % e for e in v.split("|")] if v else []
        return _value


class ArrayBool(Variant[List[bool]]):
    @field_validator("value", mode="before")
    @classmethod
    def convert_value(cls, v: str):
        _value = [e != "FALSE" for e in v.split("|")] if v else []
        return _value


class Dict(Variant[dict]):
    def local_strs(self):
        localizeds = set()
        if self.type_define.is_localization:
            for k, e in self.value.items():
                if isinstance(e, str):
                    localizeds.add(e)
        return localizeds

    @field_validator("value", mode="before")
    @classmethod
    def convert_value(cls, v: str):
        _value = eval(f'{{{v.replace("|",",")}}}') if v else {}
        return _value


# endregion


class TypeName(enum.Enum, str):
    ID = "id"
    STRING = "string"
    INT = "int"
    FLOAT = "float"
    BOOL = "bool"
    ARRAY = "array"
    ARRAY_STR = "array_str"
    ARRAY_BOOL = "array_bool"
    DICT = "dict"
    FUNCTION = "function"


class Converter:
    """
    字段转换器，将excel字段值转python数据
    """

    def __init__(self) -> None:
        self._vaiant_map: dict[str, Type[Variant]] = {}
        self.functions: list[Variant] = []

        self.register(TypeName.ID, Int)
        self.register(TypeName.STRING, String)
        self.register(TypeName.INT, Int)
        self.register(TypeName.FLOAT, Float)
        self.register(TypeName.BOOL, Bool)
        self.register(TypeName.ARRAY, Array)
        self.register(TypeName.ARRAY_STR, ArrayStr)
        self.register(TypeName.ARRAY_BOOL, ArrayBool)
        self.register(TypeName.DICT, Dict)
        self.register(TypeName.FUNCTION, Variant)

    def register(self, type: str, variant_type: Type[Variant]):
        self._vaiant_map[type] = variant_type

    def __call__(
        self,
        id: Any,
        type_define: TypeDefine,
        field_name: str,
        value: Any,
    ) -> Variant:
        variant = self._vaiant_map.get(type_define.type_name, Variant[str])
        result = variant(
            id=id, type_define=type_define, field_name=field_name, value=value
        )
        return result
