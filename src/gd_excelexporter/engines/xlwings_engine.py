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
from gd_excelexporter.core.engine import Engine
from gd_excelexporter.core.models import RawTable, RawTableMap
from gd_excelexporter.config import Configuration


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

    def _excel2rawtablemap(self, excel_filename: str) -> RawTableMap:
        with self.books.open(excel_filename) as book:
            rawtablemap: RawTableMap = {}

            sheets: Iterable[Sheet] = book.sheets

            for sheet in sheets:
                sheet: Sheet
                rawtable: RawTable = []

                rawtable = sheet.range("A1").expand().raw_value
                rawtablemap[sheet.name] = rawtable

            return rawtablemap
