"""
author:        kaluluosi111 <kaluluosi@gmail.com>
date:          2024-04-16 11:13:03
Copyright © Kaluluosi All rights reserved
"""

from pydantic import field_validator
from gd_excelexporter.core.converter import Variant


class String(Variant[str]):
    def local_strs(self):
        localizeds = set()
        if self.type_define.is_localization:
            localizeds.add(self.value)
        return localizeds

    @field_validator("value", mode="before")
    @classmethod
    def convert_value(cls, v):
        return str(v) if v else ""
