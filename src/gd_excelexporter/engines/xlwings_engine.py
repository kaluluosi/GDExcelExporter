"""
author:        kaluluosi111 <kaluluosi@gmail.com>
date:          2024-04-15 16:52:05
Copyright © Kaluluosi All rights reserved
"""

import sys
import xlwings as xw
import logging
from typing import Iterable
from xlwings.main import Sheet
from win32com import client
from gd_excelexporter.base.engine import Engine
from gd_excelexporter.base.generator import Table
from gd_excelexporter.config import Configuration
from gd_excelexporter.converter import Converter, TypeDefine, Variant
from gd_excelexporter.models import SheetData

logger = logging.getLogger(__name__)


class XlwingsEngine(xw.App, Engine):
    COM_EXCEL = "Excel.Application"
    COM_WPS = "ket.Application"

    def __init__(self, config: Configuration) -> None:
        xw.App.__init__(self, visible=False)
        Engine.__init__(self, config)
        # 设置使用的COM组件
        self.setup_com()

    def setup_com(self):
        # 判断是否是win操作系统
        if sys.platform == "win32":
            try:
                # 尝试访问Excel Com
                client.DispatchEx("Excel.Application")
            except Exception:
                logger.info("系统中没有安装Excel，尝试改为WPS")
                try:
                    _wps = client.DispatchEx("ket.Application")
                    _xl = xw._xlwindows.COMRetryObjectWrapper(_wps)
                    impl = xw._xlwindows.App(visible=False, add_book=False, xl=_xl)
                    self.impl = impl
                except Exception:
                    logger.info("系统中没有安装WPS")
        else:
            # 不是windows系统，那么就用xlwings的默认COM组件
            # xlwings支持mac，这样应该能够在mac上运行
            pass

    def _excel2dict(self, excel_filename: str) -> "dict[str, Table]":
        with self.books.open(excel_filename) as book:
            ignore_sheet_mark = self.config.ignore_sheet_mark
            # 过滤掉打了忽略标志的sheet
            sheets: Iterable[Sheet] = filter(
                lambda sheet: not sheet.name.startswith(ignore_sheet_mark), book.sheets
            )

            # sheetname->SheetData
            excel_tables: dict[str, SheetData] = {}

            # 先讲sheet转sheet_data
            for sheet in sheets:
                sheet_data = SheetData()
                row_values = sheet.range("A1").expand().raw_value

                sheet_data.define.type = list(row_values[0])
                sheet_data.define.desc = list(row_values[1])
                sheet_data.define.name = list(row_values[2])

                sheet_data.table = list([list(row) for row in row_values[3:]])
                # 找出所有被打了忽略标记的字段
                for col, field in enumerate(sheet_data.define.name):
                    # 跳过没命令的字段

                    if field is None or field.startswith(self.config.ignore_field_mark):  # noqa
                        del sheet_data.define.type[col]
                        del sheet_data.define.desc[col]
                        del sheet_data.define.name[col]
                        for row in sheet_data.table:
                            del row[col]

                excel_tables[sheet.name] = sheet_data

            cvt = Converter()

            tables: dict[str, Table] = {}

            for sheet_name, sheet_data in excel_tables.items():
                field_names = sheet_data.define.name
                field_types = sheet_data.define.type
                table = {}

                for row in sheet_data.table:
                    id_type = TypeDefine.from_str(field_types[0])
                    id_name = field_names[0]
                    id_value = row[0]
                    id = cvt(id_value, id_type, id_name, id_value)

                    row_data = {}

                    for index, value in enumerate(row):
                        field_name: str = field_names[index]
                        field_type = TypeDefine.from_str(field_types[index])
                        variant: Variant = cvt(id.value, field_type, field_name, value)
                        row_data[field_name] = variant
                        self.localized_strs = self.localized_strs.union(
                            variant.local_strs()
                        )

                    table[id.value] = row_data
                tables[sheet_name] = table

            return tables
