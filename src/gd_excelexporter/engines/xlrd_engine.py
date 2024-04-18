"""
author:        kaluluosi111 <kaluluosi@gmail.com>
date:          2024-04-15 22:35:58
Copyright © Kaluluosi All rights reserved
"""

from typing import Iterable
import xlrd
from xlrd import Book
from xlrd.sheet import Sheet

from gd_excelexporter.core.engine import Engine
from gd_excelexporter.config import Configuration
from gd_excelexporter.core.models import RawTableMap, RawTable


class XlrdEngine(Engine):
    def __init__(self, config: Configuration) -> None:
        super().__init__(config)

    def _excel2rawtablemap(self, excel_filename: str) -> RawTableMap:
        with xlrd.open_workbook(excel_filename) as book:
            rawtablemap: RawTableMap = {}

            sheets: Iterable[Sheet] = book.sheets()

            for sheet in sheets:
                sheet: Sheet

                rawtable: RawTable = []

                for row in range(sheet.nrows):
                    row_values = sheet.row_values(row)
                    rawtable.append(row_values)

                rawtablemap[sheet.name] = rawtable

            book.release_resources()
            del book
            return rawtablemap
