import glob
import os
import logging
import textwrap
import jinja2
import pkg_resources
from excelexporter.config import Configuration
from excelexporter.sheetdata import SheetData
from excelexporter.generator import Variant
from excelexporter.generator import Type


# 导出格式
extension = "gd"


def converter(var: Variant):
    type_define = var.type_define
    if var.type_define.type_name == Type.STRING:
        if type_define.is_localization:
            return f"tr('{var.value}')"
        else:
            return f"'{var.value}'"

    return var.value


def generator(sheetdata: SheetData, config: Configuration):
    loader = jinja2.FileSystemLoader(
        pkg_resources.resource_filename(__package__, ""))
    env = jinja2.Environment(autoescape=True, loader=loader)
    env.filters["cvt"] = converter
    # 表格数据脚本模板
    template = env.get_template("template.gd")
    code = template.render(sheetdata=sheetdata)
    return code


def completed_hook(config: Configuration):
    pass
