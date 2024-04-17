"""
author:        kaluluosi111 <kaluluosi@gmail.com>
date:          2024-04-16 18:11:15
Copyright © Kaluluosi All rights reserved
"""

import unittest
import unittest.mock
import sys

from gd_excelexporter.config import Configuration
from gd_excelexporter.core.engine import Engine


class TestXlwingsEngine(unittest.TestCase):
    @unittest.skipIf(sys.platform.startswith("linux"), reason="跳过linux平台测试")
    def test_excel2rawtablemap(self):
        with unittest.mock.patch(
            "gd_excelexporter.config.Configuration"
        ) as mock_config:
            engine = Engine.create_engine("xlwings", config=mock_config)

            rawtablemap = engine._excel2rawtablemap(r"test\assets\示例.xlsx")

            self.assertGreater(len(rawtablemap), 0)

    @unittest.skipIf(sys.platform.startswith("linux"), reason="跳过linux平台测试")
    def test_excel2tablemap(self):
        config = Configuration()
        engine = Engine.create_engine("xlwings", config)

        tablemap = engine._excel2tablemap(r"test\assets\示例.xlsx")

        self.assertGreater(len(tablemap), 0)

        self.assertTrue("~首页" not in tablemap)
        table = tablemap["示例-demo"]
        row = table[1]
        self.assertGreater(len(row), 0)
        self.assertTrue("*string" not in row)


class TestXlrdEngine(unittest.TestCase):
    def test_excel2rawtablemap(self):
        with unittest.mock.patch(
            "gd_excelexporter.config.Configuration"
        ) as mock_config:
            engine = Engine.create_engine("xlwings", config=mock_config)

            rawtablemap = engine._excel2rawtablemap(r"test\assets\示例.xlsx")

            self.assertGreater(len(rawtablemap), 0)

    def test_excel2tablemap(self):
        config = Configuration()
        engine = Engine.create_engine("xlrd", config)

        tablemap = engine._excel2tablemap(r"test\assets\示例.xlsx")

        self.assertGreater(len(tablemap), 0)

        self.assertTrue("~首页" not in tablemap)
        table = tablemap["示例-demo"]
        row = table[1]
        self.assertGreater(len(row), 0)
        self.assertTrue("*string" not in row)
