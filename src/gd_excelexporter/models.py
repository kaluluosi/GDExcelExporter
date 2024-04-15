import re
from pydantic import BaseModel, Field
from typing import ClassVar, List


class TypeDefine(BaseModel):
    """
    # string(params)
    functioN(params)
    [#]<type_name>[(params)]

    字段转换器要如何使用这些属性字段全靠他们自己定义了
    """

    TYPE_DEFINE_PATTERN: ClassVar[str] = (
        r"(?P<local>#?)(?P<type_name>\w+)(?P<params>\(.*\))?"
    )
    is_localization: bool  # 是否需要支持多语言，由具体的Parser去决定如何支持
    type_name: str
    params: str  # params是(a,b,c=null) 这样的字符串

    @classmethod
    def from_str(cls, define_str: str) -> "TypeDefine":
        type_define = define_str.strip()  # 先去头去尾空格
        m = re.match(cls.TYPE_DEFINE_PATTERN, type_define)
        if m:
            is_localization = m.group("local") == "#"
            type_name = m.group("type_name")
            params = m.group("params") or "(args=[])"
            return TypeDefine(
                is_localization=is_localization, type_name=type_name, params=params
            )
        raise ValueError(f"{define_str} 格式错误！")


class Define(BaseModel):
    type: List[str] = Field(default_factory=list)
    desc: List[str] = Field(default_factory=list)
    name: List[str] = Field(default_factory=list)


class SheetData(BaseModel):
    define: Define = Field(default_factory=Define)
    table: list = Field(default_factory=list)
