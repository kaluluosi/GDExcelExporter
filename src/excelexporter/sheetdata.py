import re
from dataclasses import dataclass, field
from typing import List


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
        params = m.group("params") or "(args=[])"
        return TypeDefine(
            is_localization,
            type_name,
            params
        )


@dataclass
class Define:
    type: List[TypeDefine] = field(default_factory=list)
    desc: List[str] = field(default_factory=list)
    name: List[str] = field(default_factory=list)


@dataclass
class SheetData:
    define: Define = field(default_factory=Define)
    table: list = field(default=list)
