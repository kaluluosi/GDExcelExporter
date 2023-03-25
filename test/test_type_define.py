import unittest
from excelexporter.generator import TypeDefine


class TestFieldParser(unittest.TestCase):

    def test_parse_valid_field_define(self):

        define = TypeDefine.from_str("string")
        self.assertFalse(define.is_localization)
        self.assertEqual(define.type_name, "string")
        self.assertFalse(define.params)

        define = TypeDefine.from_str("#string")
        self.assertTrue(define.is_localization)
        self.assertEqual(define.type_name, "string")
        self.assertFalse(define.params)

        define = TypeDefine.from_str("#string(a,b,c=null)")
        self.assertTrue(define.is_localization)
        self.assertEqual(define.type_name, "string")
        self.assertEqual(define.params, "(a,b,c=null)")

        define = TypeDefine.from_str("#string(a,b,c=null")
        self.assertTrue(define.is_localization)
        self.assertEqual(define.type_name, "string")
        self.assertFalse(define.params)
