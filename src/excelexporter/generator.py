import logging

from .sheetdata import SheetData
from .config import Configuration
from typing import Any, Callable


Generator = Callable[[SheetData, Configuration], str]
CompletedHook = Callable[[Configuration], None]

ConvertFunc = Callable[[Any, str, int, dict], str]

logger = logging.getLogger()


class Type:
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

    def __init__(self) -> None:
        self._map = {}

    def default(self, v, fn, id, params): return v or 0

    def register(self, type: str, cvt_method: ConvertFunc):
        self._map[type] = cvt_method

    def __call__(
            self,
            type: str,
            value: Any,
            field_name: str,
            id: int,
            *args: Any,
            **kwds: Any
    ) -> Any:
        type = type.strip()
        type_name, params = type.split("#") if "#" in type else (type, None)
        cvt = self._map.get(type_name, self.default)
        result = cvt(value, field_name, id, params)
        return result
