import unittest
from excelexporter.config import Configuration
from excelexporter.engine import Engine


class TestEngine(unittest.TestCase):

    def test_excel_to_dict(self):

        engine = Engine(Configuration())
        data = engine._excel2dict(
            r"src\excelexporter\template\sample\示例.xlsx"
        )
        print(data)
