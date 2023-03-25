from dataclasses import dataclass
import re
import logging

from .sheetdata import SheetData
from .config import Configuration
from typing import Any, Callable


Generator = Callable[[SheetData, Configuration], str]
CompletedHook = Callable[[Configuration], None]

ConvertFunc = Callable[[Any, str, int, dict], str]

logger = logging.getLogger()


@dataclass
class TypeDefine:
    """
    # string(params)
    functioN(params)
    [#]<type_name>[(params)]

    字段转换器要如何使用这些属性字段全靠他们自己定义了
    """
    TYPE_DEFINE_PATTERN = r"(?P<local>#?)(?P<type_name>\w+)(?P<params>\(.*\))?"
    is_localization: bool  # 是否需要支持多语言，由具体的Parser去决定如何支持
    type_name: str
    params: str  # params是(a,b,c=null) 这样的字符串

    @classmethod
    def from_str(self, define_str: str) -> 'TypeDefine':
        type_define = define_str.strip()  # 先去头去尾空格
        m = re.match(self.TYPE_DEFINE_PATTERN, type_define)
        is_localization = m.group("local")
        type_name = m.group("type_name")
        params = m.group("params")
        return TypeDefine(
            is_localization,
            type_name,
            params
        )


@dataclass
class Variant:
    id: int
    type_define: TypeDefine
    field_name: str
    value: Any


class String(Variant):
    @staticmethod
    def make(id, td, fn, v):
        value = str(v) if v else ""
        return String(id, td, fn, value)


class Int(Variant):
    @staticmethod
    def make(id, td, fn, v):
        value = int(float(v or 0))
        return Int(id, td, fn, value)


class Float(Variant):
    @staticmethod
    def make(id, td, fn, v):
        value = float(v or 0)
        return Float(id, td, fn, value)


class Bool(Variant):
    @staticmethod
    def make(id, td, fn, v):
        value = v != "FALSE"
        return Bool(id, td, fn, value)


class Array(Variant):
    @staticmethod
    def make(id, td, fn, v):
        value = eval(f'[{v.replace("|",",")}]') if v else []
        return Array(id, td, fn, value)


class ArrayStr(Variant):
    @staticmethod
    def make(id, td, fn, v):
        value = ["%s" % e for e in v.split("|")]if v else []
        return ArrayStr(id, td, fn, value)


class ArrayBool(Variant):

    @staticmethod
    def make(id, td, fn, v):
        value = [e != "FALSE" for e in v.split("|")] if v else []
        return ArrayBool(id, td, fn, value)


class Dict(Variant):
    @staticmethod
    def make(id, td, fn, v):
        value = eval(f'{{{v.replace("|",",")}}}') if v else {}
        return Dict(id, td, fn, value)


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

    def default(self, id, td, fn, value): return value or 0

    def register(self, type: str, self_method: ConvertFunc):
        self._map[type] = self_method

    def __call__(
            self,
            id: int,
            type_define: TypeDefine,
            field_name: str,
            value: Any,
            *args: Any,
            **kwds: Any
    ) -> Any:
        cvt = self._map.get(type_define.type_name, self.default)
        result = cvt(id, type_define, field_name, value)
        return result
