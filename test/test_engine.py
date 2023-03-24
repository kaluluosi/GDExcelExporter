import unittest
from excelexporter.config import Configuration
from excelexporter.engine import Engine


class TestEngine(unittest.TestCase):

    def test_excel_to_dict(self):

        engine = Engine(Configuration())
        data = engine._excel2dict(
            r"src\excelexporter\template\sample\示例.xlsx")

        self.assertTrue("示例-demo" in data)

        sheetdata = data.get("示例-demo")

        id_field_type = sheetdata.define.type[0]

        self.assertFalse(id_field_type.is_localization)
        self.assertEqual(id_field_type.type_name, "int")
        self.assertFalse(id_field_type.params)

        id_field_name = sheetdata.define.name[0]
        self.assertEqual(id_field_name, "id")

        function_field_type = sheetdata.define.type[10]
        self.assertFalse(function_field_type.is_localization)
        self.assertEqual(function_field_type.type_name, "function")
        self.assertTrue(function_field_type.params)
