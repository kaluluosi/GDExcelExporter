import unittest
from unittest import mock
from excelexporter.generator import Converter, TypeDefine


class TestConverter(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.cvt = Converter()

    def test_default_cvt(self):
        self.cvt.default = mock.MagicMock(return_value=1)

        result = self.cvt(0, TypeDefine.from_str("abaaba"), "shit", 1)

        self.cvt.default.assert_called_once()
        self.assertEqual(result, 1)

    def test_string_cvt(self):
        result = self.cvt(0, TypeDefine.from_str("string"), "name", "Tom")
        self.assertEqual(result.value, "Tom")

    def test_function_cvt(self):
        result = self.cvt(0, TypeDefine.from_str(
            "function"), "func", "print('hello')")
        self.assertEqual(result.value, "print('hello')")
        self.assertEqual(result.type_define.params, "()")
        self.assertEqual(result.type_define.type_name, "function")

    def test_function_with_params_cvt(self):
        result = self.cvt(0, TypeDefine.from_str(
            "function(a,b,c)"), "func", "print('hello')")
        self.assertEqual(result.value, "print('hello')")
        self.assertEqual(result.type_define.params, "(a,b,c)")
        self.assertEqual(result.type_define.type_name, "function")
