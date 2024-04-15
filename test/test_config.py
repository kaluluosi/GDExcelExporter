import os
import unittest
import tempfile

import toml
from gd_excelexporter.config import Configuration


class TestConfig(unittest.TestCase):
    def test_create_config(self):
        config = Configuration()

        config = Configuration(
            ignore_sheet_mark="!",
            ignore_field_mark="*",
            custom_generator="1",
            input="a",
            output="b",
            project_root="c",
        )

        config.ignore_field_mark = "#"

    def test_save_load(self):
        config = Configuration()

        with tempfile.TemporaryDirectory() as dirname:
            temp = os.path.join(dirname, "config.toml")
            config.save(temp)
            new_config: Configuration = Configuration.load(temp)
            self.assertEqual(
                config.ignore_field_mark,
                new_config.ignore_field_mark,
                "ignore_field_mark should be equal",
            )

            self.assertTrue(
                config.localization.babel_keywords, "babel keywords should not be empty"
            )

    def test_load_wrong_format(self):
        with tempfile.NamedTemporaryFile(mode="w+", delete=False) as tmp:
            tmp.write("xxx")
            tmp.seek(0)
            self.assertRaises(toml.TomlDecodeError, Configuration.load, tmp.name)

    def test_load_not_exist(self):
        self.assertRaises(FileNotFoundError, Configuration.load, "xxx.ee")
