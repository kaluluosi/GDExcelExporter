from pydantic import BaseModel, Field
from typing import Any, Dict, List

# 已经导出成dict的表数据
Table = Dict[int, Dict[str, Any]]
TableMap = Dict[str, Table]
# 原始表数据，直接读取自sheet的原始数据，没有进行类型转换和加工的。
RawTable = List[List[str]]
# 原始表map，sheet名为key，原始表数据为value
RawTableMap = Dict[str, RawTable]


class Defines(BaseModel):
    type: List[str] = Field(
        default_factory=list,
        description="类型定义行，对应sheet表第一行，见`示例.xlsx`第一行粉色",
    )
    desc: List[str] = Field(
        default_factory=list,
        description="字段描述行，对应sheet表第二行，见`示例.xlsx`第二行黑色",
    )
    name: List[str] = Field(
        default_factory=list,
        description="字段名行，对应sheet表第三行，见`示例.xlsx`第三行黄色",
    )
