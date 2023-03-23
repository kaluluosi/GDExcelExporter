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
        self.register(Type.STRING, lambda v, n, id, p: str(v) if v else "")
        self.register(
            Type.INT, lambda v, n, id, p: int(str(v or 0).split(".")[0])
        )
        self.register(Type.FLOAT, lambda v, n, id, p: float(str(v or 0)))
        self.register(Type.BOOL, lambda v, n, id, p: v != "FALSE")
        self.register(
            Type.ARRAY,
            lambda v, n, id, p: eval(f'[{v.replace("|",",")}]') if v else []
        )
        self.register(
            Type.ARRAY_STR,
            lambda v, n, id, p: ["%s" %
                                 e for e in v.split("|")]if v else []
        )
        self.register(
            Type.ARRAY_BOOL,
            lambda v, n, id, p: [
                e != "FALSE" for e in v.split("|")] if v else []
        )
        self.register(
            Type.DICT,
            lambda v, n, id, p: eval(f'{{{v.replace("|",",")}}}')
            if v else {}
        )

    def default(self, v, fn, id, params): return v or 0

    def register(self, type: str, self_method: ConvertFunc):
        self._map[type] = self_method

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
