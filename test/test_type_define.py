from typing import Type
import unittest
import sys

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

        string_td_cls: Type[String] = self.tds["string"].load()

        string_td = string_td_cls(type_txt="string")
        value = string_td.convert("shit")
        self.assertEqual(value, "shit")

        value = string_td.convert(None)
        self.assertEqual(value, "")
        value = string_td.convert("")
        self.assertEqual(value, "")

    def test_int(self):
        int_td_cls: Type[Int] = self.tds["int"].load()
        int_td = int_td_cls(type_txt="int")
        value = int_td.convert("123")
        self.assertEqual(value, 123)

        value = int_td.convert(None)
        self.assertEqual(value, 0)
        value = int_td.convert("")
        self.assertEqual(value, 0)

    def test_float(self):
        float_td_cls: Type[Float] = self.tds["float"].load()
        float_td = float_td_cls(type_txt="float")
        value = float_td.convert("123.456")
        self.assertEqual(value, 123.456)
        value = float_td.convert(None)
        self.assertEqual(value, 0.0)
        value = float_td.convert("")
        self.assertEqual(value, 0.0)

    def test_dict(self):
        dict_td_cls: Type[Dict] = self.tds["dict"].load()
        dict_td = dict_td_cls(type_txt="dict")
        value = dict_td.convert('"a": 1|"b": 2')
        self.assertEqual(value, {"a": 1, "b": 2})

        value = dict_td.convert(None)
        self.assertEqual(value, {})
        value = dict_td.convert("")
        self.assertEqual(value, {})

    def test_bool(self):
        bool_td_cls: Type[Bool] = self.tds["bool"].load()
        bool_td = bool_td_cls(type_txt="bool")
        value = bool_td.convert("true")
        self.assertEqual(value, True)
        value = bool_td.convert(None)
        self.assertEqual(value, False)
        value = bool_td.convert("")
        self.assertEqual(value, False)

    def test_array(self):
        array_td_cls: Type[Array] = self.tds["array"].load()
        array_td = array_td_cls(type_txt="array")
        value = array_td.convert("'a'|'b'|'c'")
        self.assertEqual(value, ["a", "b", "c"])
        value = array_td.convert(None)
        self.assertEqual(value, [])
        value = array_td.convert("")
        self.assertEqual(value, [])

    def test_array_string(self):
        array_str_td_cls: Type[ArrayStr] = self.tds["array_str"].load()
        array_str_td = array_str_td_cls(type_txt="array_str")
        value = array_str_td.convert("a|b|c")
        self.assertEqual(value, ["a", "b", "c"])
        value = array_str_td.convert(None)
        self.assertEqual(value, [])
        value = array_str_td.convert("")
        self.assertEqual(value, [])

    def test_array_bool(self):
        array_bool_td_cls: Type[ArrayBool] = self.tds["array_bool"].load()
        array_bool_td = array_bool_td_cls(type_txt="array_bool")
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
        function_td_cls: Type[Function] = self.tds["function"].load()
        function_td = function_td_cls(type_txt="function")
        value = function_td.convert("print(123)")
        self.assertEqual(value, "print(123)")
        value = function_td.convert(None)
        self.assertEqual(value, "pass")
        value = function_td.convert("")
        self.assertEqual(value, "pass")

    def test_tr_string(self):
        tr_string_td_cls: Type[TrString] = self.tds["tr_string"].load()
        tr_string_td = tr_string_td_cls(type_txt="tr_string")
        value = tr_string_td.convert("123")
        self.assertEqual(value, "123")
        value = tr_string_td.convert(None)
        self.assertEqual(value, "")
        value = tr_string_td.convert("")
        self.assertEqual(value, "")

    def test_tr_array_str(self):
        tr_array_str_td_cls: Type[TrArrayStr] = self.tds["tr_array_str"].load()
        tr_array_str_td = tr_array_str_td_cls(type_txt="tr_array_str")
        value = tr_array_str_td.convert("a|b|c")
        self.assertEqual(value, ["a", "b", "c"])
        value = tr_array_str_td.convert(None)
        self.assertEqual(value, [])
        value = tr_array_str_td.convert("")
        self.assertEqual(value, [])

    def test_tr_dick(self):
        tr_dict_str_td_cls: Type[TrDict] = self.tds["tr_dict"].load()
        tr_dict_str_td = tr_dict_str_td_cls(type_txt="tr_dict")
        value = tr_dict_str_td.convert('"name":"Tom"|"age":10')
        self.assertEqual(value, {"name": "Tom", "age": 10})
        value = tr_dict_str_td.convert(None)
        self.assertEqual(value, {})
        value = tr_dict_str_td.convert("")
        self.assertEqual(value, {})
