
from .sheetdata import SheetData
from .config import Configuration
from typing import Any, Callable


Generator = Callable[[SheetData, Configuration], str]
CompletedHook = Callable[[Configuration], None]

ConvertFunc = Callable[[Any, str, int], str]


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

    _map = {}

    def default(self, v, n, id): return v or 0

    @classmethod
    def register(cls, type: str, cvt_method: ConvertFunc):
        cls._map[type] = cvt_method

    def __call__(
            self,
            type: str,
            value: Any,
            name: str,
            id: int,
            *args: Any,
            **kwds: Any
    ) -> Any:
        cvt = self._map.get(type, self.default)
        return cvt(value, name, id)
