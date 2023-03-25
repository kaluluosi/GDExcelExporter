import glob
import os
import logging
import textwrap
import jinja2
import pkg_resources
from excelexporter.config import Configuration
from excelexporter.sheetdata import SheetData


# 导出格式
extension = "gd"


def generator(sheetdata: SheetData, config: Configuration):
    # 表格数据脚本模板
    temp_ctn = pkg_resources.resource_string(
        __package__, "template.gd").decode()
    template = jinja2.Template(temp_ctn)
    code = template.render(sheetdata=sheetdata)
    return code


def completed_hook(config: Configuration):
    pass
