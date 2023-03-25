from dataclasses import dataclass
import logging

from excelexporter.sheetdata import SheetData, TypeDefine
from excelexporter.config import Configuration
from typing import Any, Callable


Generator = Callable[[SheetData, Configuration], str]
CompletedHook = Callable[[Configuration], None]

ConvertFunc = Callable[[Any, str, int, dict], str]

logger = logging.getLogger()


@dataclass
class Variant:

    id: int
    type_define: TypeDefine
    field_name: str
    value: Any

    def local_strs(self):
        return set()


class String(Variant):
    @staticmethod
    def make(id: Any, td: TypeDefine, fn: str, v: Any):
        value = str(v) if v else ""
        return String(id, td, fn, value)

    def local_strs(self):
        localizeds = set()
        if self.type_define.is_localization:
            localizeds.add(self.value)
        return localizeds


class Int(Variant):
    @staticmethod
    def make(id: Any, td: TypeDefine, fn: str, v: Any):
        value = int(float(v or 0))
        return Int(id, td, fn, value)


class Float(Variant):
    @staticmethod
    def make(id: Any, td: TypeDefine, fn: str, v: Any):
        value = float(v or 0)
        return Float(id, td, fn, value)


class Bool(Variant):
    @staticmethod
    def make(id: Any, td: TypeDefine, fn: str, v: Any):
        value = v != "FALSE"
        return Bool(id, td, fn, value)


class Array(Variant):
    @staticmethod
    def make(id: Any, td: TypeDefine, fn: str, v: Any):
        value = eval(f'[{v.replace("|",",")}]') if v else []
        return Array(id, td, fn, value)

    def local_strs(self):
        localizeds = set()
        if self.type_define.is_localization:
            for e in self.value:
                if isinstance(e, str):
                    localizeds.add(e)
        return localizeds


class ArrayStr(Variant):
    @staticmethod
    def make(id: Any, td: TypeDefine, fn: str, v: Any):
        value = ["%s" % e for e in v.split("|")]if v else []
        return ArrayStr(id, td, fn, value)

    def local_strs(self):
        localizeds = set()
        if self.type_define.is_localization:
            for e in self.value:
                if isinstance(e, str):
                    localizeds.add(e)
        return localizeds


class ArrayBool(Variant):

    @staticmethod
    def make(id: Any, td: TypeDefine, fn: str, v: Any):
        value = [e != "FALSE" for e in v.split("|")] if v else []
        return ArrayBool(id, td, fn, value)


class Dict(Variant):
    @staticmethod
    def make(id: Any, td: TypeDefine, fn: str, v: Any):
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
