import unittest
from unittest import mock
from excelexporter.generator import Converter, Type


class TestConverter(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        Converter.register(
            Type.STRING,
            lambda v, fn, id, params: Type.STRING
        )
        Converter.register(
            Type.INT,
            lambda v, fn, id, params: Type.INT
        )
        Converter.register(
            Type.FLOAT,
            lambda v, fn, id, params: Type.FLOAT
        )
        Converter.register(
            Type.BOOL,
            lambda v, fn, id, params: Type.BOOL
        )
        Converter.register(
            Type.ARRAY,
            lambda v, fn, id, params: Type.ARRAY
        )
        Converter.register(
            Type.ARRAY_STR,
            lambda v, fn, id, params: Type.ARRAY_STR
        )
        Converter.register(
            Type.ARRAY_BOOL,
            lambda v, fn, id, params: Type.ARRAY_BOOL
        )
        Converter.register(
            Type.DICT,
            lambda v, fn, id, params: Type.DICT
        )
        Converter.register(
            Type.FUNCTION,
            lambda v, fn, id, params: (Type.FUNCTION, params)
        )

        cls.converter = Converter()

    def test_default_cvt(self):
        self.converter.default = mock.MagicMock(return_value=1)

        result = self.converter(
            "shit",
            "wrong value",
            "my field",
            1
        )

        self.converter.default.assert_called_once_with(None, "my field", 1)
        self.assertEqual(result, 1)

    def test_string_cvt(self):
        result = self.converter(
            Type.STRING,
            "你好",
            "desc",
            1
        )
        self.assertEqual(result, Type.STRING)

    def test_function_cvt(self):

        result = self.converter(
            Type.FUNCTION,
            "print(args[0])",
            "callback",
            1
        )
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], Type.FUNCTION)

    def test_function_with_params_cvt(self):
        result = self.converter(
            "function#(a,b,c)",
            "print(a)",
            "callback",
            1
        )
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], Type.FUNCTION)
        self.assertEqual(result[1], "(a,b,c)")
