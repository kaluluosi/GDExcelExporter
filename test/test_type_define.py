from typing import Type
import unittest
import sys

from gd_excelexporter.core.type_define import TypeDefine
from gd_excelexporter.type_defines import (
    String,
    Int,
    Float,
    Dict,
    Bool,
    Array,
    ArrayStr,
    ArrayBool,
    Function,
    TrString,
    TrArrayStr,
    TrDict,
)

if sys.version_info < (3, 10):
    from importlib_metadata import entry_points
else:
    from importlib.metadata import entry_points


class TestConverter(unittest.TestCase):
    def setUp(self) -> None:
        tds = entry_points(group="gd_excelexporter.type_define")
        self.assertGreater(len(tds), 0)

        self.tds = tds

    def test_load_type_define(self):
        """
        测试加载所有类型定义插件
        """
        for type_name in self.tds.names:
            self.tds[type_name].load()

    def test_string(self):
        """
        测试string定义和转换
        """
        string_td = TypeDefine.from_str("string")
        value = string_td.convert("shit")
        self.assertEqual(value, "shit")

        value = string_td.convert(None)
        self.assertEqual(value, "")
        value = string_td.convert("")
        self.assertEqual(value, "")

    def test_int(self):
        int_td = TypeDefine.from_str("int")
        value = int_td.convert("123")
        self.assertEqual(value, 123)

        value = int_td.convert(None)
        self.assertEqual(value, 0)
        value = int_td.convert("")
        self.assertEqual(value, 0)

    def test_float(self):
        float_td = TypeDefine.from_str("float")
        value = float_td.convert("123.456")
        self.assertEqual(value, 123.456)
        value = float_td.convert(None)
        self.assertEqual(value, 0.0)
        value = float_td.convert("")
        self.assertEqual(value, 0.0)

    def test_dict(self):
        dict_td = TypeDefine.from_str("dict")
        value = dict_td.convert('"a": 1|"b": 2')
        self.assertEqual(value, {"a": 1, "b": 2})

        value = dict_td.convert(None)
        self.assertEqual(value, {})
        value = dict_td.convert("")
        self.assertEqual(value, {})

    def test_bool(self):
        bool_td = TypeDefine.from_str("bool")
        value = bool_td.convert("true")
        self.assertEqual(value, True)
        value = bool_td.convert(None)
        self.assertEqual(value, False)
        value = bool_td.convert("")
        self.assertEqual(value, False)

    def test_array(self):
        array_td = TypeDefine.from_str("array")
        value = array_td.convert("'a'|'b'|'c'")
        self.assertEqual(value, ["a", "b", "c"])
        value = array_td.convert(None)
        self.assertEqual(value, [])
        value = array_td.convert("")
        self.assertEqual(value, [])

    def test_array_string(self):
        array_str_td = TypeDefine.from_str("array_str")
        value = array_str_td.convert("a|b|c")
        self.assertEqual(value, ["a", "b", "c"])
        value = array_str_td.convert(None)
        self.assertEqual(value, [])
        value = array_str_td.convert("")
        self.assertEqual(value, [])

    def test_array_bool(self):
        array_bool_td = TypeDefine.from_str("array_bool")
        value = array_bool_td.convert("true|false|true")
        self.assertEqual(value, [True, False, True])
        value = array_bool_td.convert("TRUE|FALSE|TRUE")
        self.assertEqual(value, [True, False, True])
        value = array_bool_td.convert("是|否|是")
        self.assertEqual(value, [True, False, True])
        value = array_bool_td.convert(None)
        self.assertEqual(value, [])
        value = array_bool_td.convert("")
        self.assertEqual(value, [])

    def test_function(self):
        function_td = TypeDefine.from_str("function")
        value = function_td.convert("print(123)")
        self.assertEqual(value, "print(123)")
        value = function_td.convert(None)
        self.assertEqual(value, "pass")
        value = function_td.convert("")
        self.assertEqual(value, "pass")

    def test_tr_string(self):
        tr_string_td = TypeDefine.from_str("tr_string")
        value = tr_string_td.convert("123")
        self.assertEqual(value, "123")
        value = tr_string_td.convert(None)
        self.assertEqual(value, "")
        value = tr_string_td.convert("")
        self.assertEqual(value, "")

    def test_tr_array_str(self):
        tr_array_str_td = TypeDefine.from_str("tr_array_str")
        value = tr_array_str_td.convert("a|b|c")
        self.assertEqual(value, ["a", "b", "c"])
        value = tr_array_str_td.convert(None)
        self.assertEqual(value, [])
        value = tr_array_str_td.convert("")
        self.assertEqual(value, [])

    def test_tr_dick(self):
        tr_dict_str_td = TypeDefine.from_str("tr_dict")
        value = tr_dict_str_td.convert('"name":"Tom"|"age":10')
        self.assertEqual(value, {"name": "Tom", "age": 10})
        value = tr_dict_str_td.convert(None)
        self.assertEqual(value, {})
        value = tr_dict_str_td.convert("")
        self.assertEqual(value, {})
