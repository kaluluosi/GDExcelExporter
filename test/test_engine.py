"""
author:        kaluluosi111 <kaluluosi@gmail.com>
date:          2024-04-16 18:11:15
Copyright © Kaluluosi All rights reserved
"""

import unittest
import unittest.mock

from gd_excelexporter.engines.xlrd_engine import XlrdEngine
from gd_excelexporter.engines.xlwings_engine import XlwingsEngine


class TestXlwingsEngine(unittest.TestCase):
    def test_excel2rawtablemap(self):
        with unittest.mock.patch(
            "gd_excelexporter.config.Configuration"
        ) as mock_config:
            engine = XlwingsEngine(mock_config)

            rawtablemap = engine._excel2rawtablemap(r"test\assets\示例.xlsx")

            self.assertGreater(len(rawtablemap), 0)


class TestXlrdEngine(unittest.TestCase):
    def test_excel2rawtablemap(self):
        with unittest.mock.patch(
            "gd_excelexporter.config.Configuration"
        ) as mock_config:
            engine = XlrdEngine(mock_config)

            rawtablemap = engine._excel2rawtablemap(r"test\assets\示例.xlsx")

            self.assertGreater(len(rawtablemap), 0)
