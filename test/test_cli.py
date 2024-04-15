"""
author:        kaluluosi111 <kaluluosi@gmail.com>
date:          2024-04-15 07:08:01
Copyright © Kaluluosi All rights reserved
"""

import unittest
import os
import tempfile
from excelexporter.cli import main
from click.testing import CliRunner


class TestCli(unittest.TestCase):
    def setUp(self) -> None:
        os.chdir("test/settings")

    def test_init(self):
        runner = CliRunner()

        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            res = runner.invoke(main, ["init"], input="\n\n\n\n")

            self.assertFalse(res.exception)

            self.assertTrue(os.path.exists("settings"), "settings not exists")
            self.assertTrue(
                os.path.exists("settings/export.toml"), "export.toml not exists"
            )

    def test_extract(self):
        runner = CliRunner()
        res = runner.invoke(main, ["extract"])
        if res.exception:
            self.fail(res.exception.with_traceback(None))
