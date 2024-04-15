import logging

# dataclass在这里我用来作为结构体用
from dataclasses import dataclass
from excelexporter.sheetdata import SheetData, TypeDefine
from excelexporter.config import Configuration
from typing import Any, Callable, Generic, List, TypeVar


Generator = Callable[[SheetData, Configuration], str]
CompletedHook = Callable[[Configuration], None]

T = TypeVar("T")

logger = logging.getLogger()


@dataclass
class Variant(Generic[T]):
    id: int
    type_define: TypeDefine
    field_name: str
    value: T

    def local_strs(self):
        return set()


class String(Variant[str]):
    @staticmethod
    def make(id: Any, td: TypeDefine, fn: str, v: str):
        value = str(v) if v else ""
        return String(id, td, fn, value)

    def local_strs(self):
        localizeds = set()
        if self.type_define.is_localization:
            localizeds.add(self.value)
        return localizeds


class Int(Variant[int]):
    @staticmethod
    def make(id: Any, td: TypeDefine, fn: str, v: str):
        value = int(float(v or 0))
        return Int(id, td, fn, value)


class Float(Variant[float]):
    @staticmethod
    def make(id: Any, td: TypeDefine, fn: str, v: str):
        value = float(v or 0)
        return Float(id, td, fn, value)


class Bool(Variant[bool]):
    @staticmethod
    def make(id: Any, td: TypeDefine, fn: str, v: str):
        if isinstance(v, str):  # 检查 v 是否为字符串
            value = v.lower() != "false"  # 如果是字符串，将 v 转换为小写后进行比较
        else:
            value = v is not False  # 如果不是字符串，直接与 False 进行比较
        return Bool(id, td, fn, value)


class Array(Variant[list]):
    @staticmethod
    def make(id: Any, td: TypeDefine, fn: str, v: str):
        value = eval(f'[{v.replace("|",",")}]') if v else []
        return Array(id, td, fn, value)

    def local_strs(self):
        localizeds = set()
        if self.type_define.is_localization:
            for e in self.value:
                if isinstance(e, str):
                    localizeds.add(e)
        return localizeds


class ArrayStr(Variant[List[str]]):
    @staticmethod
    def make(id: Any, td: TypeDefine, fn: str, v: str):
        value = ["%s" % e for e in v.split("|")] if v else []
        return ArrayStr(id, td, fn, value)

    def local_strs(self):
        localizeds = set()
        if self.type_define.is_localization:
            for e in self.value:
                if isinstance(e, str):
                    localizeds.add(e)
        return localizeds


class ArrayBool(Variant[List[bool]]):
    @staticmethod
    def make(id: Any, td: TypeDefine, fn: str, v: str):
        value = [e != "FALSE" for e in v.split("|")] if v else []
        return ArrayBool(id, td, fn, value)


class Dict(Variant[dict]):
    @staticmethod
    def make(id: Any, td: TypeDefine, fn: str, v: str):
        value = eval(f'{{{v.replace("|",",")}}}') if v else {}
        return Dict(id, td, fn, value)

    def local_strs(self):
        localizeds = set()
        if self.type_define.is_localization:
            for k, e in self.value.items():
                if isinstance(e, str):
                    localizeds.add(e)
        return localizeds


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

    def default(self, id, td, fn, value):
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
        result = cvt(id, type_define, field_name, value)
        return result
