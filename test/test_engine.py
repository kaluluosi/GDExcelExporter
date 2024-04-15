import unittest
import os
from excelexporter.config import Configuration
from excelexporter.engine import Engine, discover_generator


class TestEngine(unittest.TestCase):
    def test_excel_to_dict(self):
        engine = Engine(Configuration())
        data = engine._excel2dict(r"test\setting\data\示例.xlsx")
        print(data)

    def test_discover_generators(self):
        generators = discover_generator()
        self.assertTrue(generators["GDS2.0"])

    @unittest.skip("not ready")
    def test_gen(self):
        file = "dist/示例/demo.gd"
        os.chdir(r"test\setting")
        config = Configuration.load()
        engine = Engine(config)

        if os.path.exists(file):
            os.remove(file)

        engine.gen_one(r"data\示例.xlsx")

        self.assertTrue(os.path.exists(file))
