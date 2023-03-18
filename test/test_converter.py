import unittest
from unittest import mock
from excelexporter.generator import Converter, Type


class TestConverter(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.cvt = Converter()
        cls.cvt.register(
            Type.STRING,
            lambda v, fn, id, params: Type.STRING
        )
        cls.cvt.register(
            Type.INT,
            lambda v, fn, id, params: Type.INT
        )
        cls.cvt.register(
            Type.FLOAT,
            lambda v, fn, id, params: Type.FLOAT
        )
        cls.cvt.register(
            Type.BOOL,
            lambda v, fn, id, params: Type.BOOL
        )
        cls.cvt.register(
            Type.ARRAY,
            lambda v, fn, id, params: Type.ARRAY
        )
        cls.cvt.register(
            Type.ARRAY_STR,
            lambda v, fn, id, params: Type.ARRAY_STR
        )
        cls.cvt.register(
            Type.ARRAY_BOOL,
            lambda v, fn, id, params: Type.ARRAY_BOOL
        )
        cls.cvt.register(
            Type.DICT,
            lambda v, fn, id, params: Type.DICT
        )
        cls.cvt.register(
            Type.FUNCTION,
            lambda v, fn, id, params: (Type.FUNCTION, params)
        )

    def test_default_cvt(self):
        self.cvt.default = mock.MagicMock(return_value=1)

        result = self.cvt(
            "shit",
            "wrong value",
            "my field",
            1
        )

        self.cvt.default.assert_called_once()
        self.assertEqual(result, 1)

    def test_string_cvt(self):
        result = self.cvt(
            Type.STRING,
            "你好",
            "desc",
            1
        )
        self.assertEqual(result, Type.STRING)

    def test_function_cvt(self):

        result = self.cvt(
            Type.FUNCTION,
            "print(args[0])",
            "callback",
            1
        )
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], Type.FUNCTION)

    def test_function_with_params_cvt(self):
        result = self.cvt(
            "function#(a,b,c)",
            "print(a)",
            "callback",
            1
        )
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], Type.FUNCTION)
        self.assertEqual(result[1], "(a,b,c)")
