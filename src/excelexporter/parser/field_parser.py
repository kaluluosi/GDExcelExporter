import re
import abc

from dataclasses import dataclass
from typing import Any


TYPE_DEFINE_PATTERN = r"(?P<local>#?)(?P<type_name>\w+)(?P<params>\(.*\))?"


@dataclass
class TypeDefine:
    """
    # string(params)
    functioN(params)
    [#]<type_name>[(params)]

    字段转换器要如何使用这些属性字段全靠他们自己定义了
    """
    is_localization: bool  # 是否需要支持多语言，由具体的Parser去决定如何支持
    type_name: str
    params: str  # params是(a,b,c=null) 这样的字符串

    @classmethod
    def from_str(self, define_str: str) -> 'TypeDefine':
        type_define = define_str.strip()  # 先去头去尾空格
        m = re.match(TYPE_DEFINE_PATTERN, type_define)
        is_localization = m.group("local")
        type_name = m.group("type_name")
        params = m.group("params")
        return TypeDefine(
            is_localization,
            type_name,
            params
        )


class FieldParser(abc.ABC):

    @abc.abstractmethod
    def parse(
            self,
            id: int,
            type_define: TypeDefine,
            field_name: str,
            value: Any
    ) -> Any:
        ...

    def __call__(
        self,
        id: int,
        type_define: str,
        field_name: str,
        value: Any
    ) -> Any:
        define = TypeDefine.from_str(type_define)
        return self.parse(id, define, field_name, value)
