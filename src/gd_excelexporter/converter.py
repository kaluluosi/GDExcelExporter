import logging

# dataclass在这里我用来作为结构体用
from pydantic import BaseModel
from gd_excelexporter.models import SheetData, TypeDefine
from gd_excelexporter.config import Configuration
from typing import Any, Callable, Generic, List, Set, TypeVar


Generator = Callable[[SheetData, Configuration], str]
CompletedHook = Callable[[Configuration], None]

T = TypeVar("T")

logger = logging.getLogger()


# region 类型转换器定义
class Variant(BaseModel, Generic[T]):
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


class String(Variant[str]):
    @staticmethod
    def make(id: Any, type_define: TypeDefine, field_name: str, value: str):
        value = str(value) if value else ""
        return String(
            id=id, type_define=type_define, field_name=field_name, value=value
        )

    def local_strs(self):
        localizeds = set()
        if self.type_define.is_localization:
            localizeds.add(self.value)
        return localizeds


class Int(Variant[int]):
    @staticmethod
    def make(id: Any, type_define: TypeDefine, field_name: str, value: str):
        _value = int(float(value or 0))
        return Int(id=id, type_define=type_define, field_name=field_name, value=_value)


class Float(Variant[float]):
    @staticmethod
    def make(id: Any, type_define: TypeDefine, field_name: str, value: str):
        _value = float(value or 0)
        return Float(
            id=id, type_define=type_define, field_name=field_name, value=_value
        )


class Bool(Variant[bool]):
    @staticmethod
    def make(id: Any, type_define: TypeDefine, field_name: str, value: str):
        if isinstance(value, str):  # 检查 value 是否为字符串
            _value = (
                value.lower() != "false"
            )  # 如果是字符串，将 value 转换为小写后进行比较
        else:
            _value = value is not False  # 如果不是字符串，直接与 False 进行比较
        return Bool(id=id, type_define=type_define, field_name=field_name, value=_value)


class Array(Variant[list]):
    @staticmethod
    def make(id: Any, type_define: TypeDefine, field_name: str, value: str):
        _value = eval(f'[{value.replace("|",",")}]') if value else []
        return Array(
            id=id, type_define=type_define, field_name=field_name, value=_value
        )

    def local_strs(self):
        localizeds = set()
        if self.type_define.is_localization:
            for e in self.value:
                if isinstance(e, str):
                    localizeds.add(e)
        return localizeds


class ArrayStr(Variant[List[str]]):
    @staticmethod
    def make(id: Any, type_define: TypeDefine, field_name: str, value: str):
        _value = ["%s" % e for e in value.split("|")] if value else []
        return ArrayStr(
            id=id, type_define=type_define, field_name=field_name, value=_value
        )

    def local_strs(self):
        localizeds = set()
        if self.type_define.is_localization:
            for e in self.value:
                if isinstance(e, str):
                    localizeds.add(e)
        return localizeds


class ArrayBool(Variant[List[bool]]):
    @staticmethod
    def make(id: Any, type_define: TypeDefine, field_name: str, value: str):
        _value = [e != "FALSE" for e in value.split("|")] if value else []
        return ArrayBool(
            id=id, type_define=type_define, field_name=field_name, value=_value
        )


class Dict(Variant[dict]):
    @staticmethod
    def make(id: Any, type_define: TypeDefine, field_name: str, value: str):
        _value = eval(f'{{{value.replace("|",",")}}}') if value else {}
        return Dict(id=id, type_define=type_define, field_name=field_name, value=_value)

    def local_strs(self):
        localizeds = set()
        if self.type_define.is_localization:
            for k, e in self.value.items():
                if isinstance(e, str):
                    localizeds.add(e)
        return localizeds


# endregion


class Type:
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
        self._map = {}
        self.functions: list[Variant] = []

        self.register(Type.ID, Int.make)
        self.register(Type.STRING, String.make)
        self.register(Type.INT, Int.make)
        self.register(Type.FLOAT, Float.make)
        self.register(Type.BOOL, Bool.make)
        self.register(Type.ARRAY, Array.make)
        self.register(Type.ARRAY_STR, ArrayStr.make)
        self.register(Type.ARRAY_BOOL, ArrayBool.make)
        self.register(Type.DICT, Dict.make)
        self.register(Type.FUNCTION, Variant)

    def default(self, id, type_define, field_name, value):
        return value or 0

    def register(self, type: str, self_method: Callable):
        self._map[type] = self_method

    def __call__(
        self,
        id: int,
        type_define: TypeDefine,
        field_name: str,
        value: Any,
        *args: Any,
        **kwds: Any,
    ) -> Any:
        cvt = self._map.get(type_define.type_name, self.default)
        result = cvt(id=id, type_define=type_define, field_name=field_name, value=value)
        return result
