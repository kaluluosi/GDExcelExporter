"""
author:        kaluluosi111 <kaluluosi@gmail.com>
date:          2024-04-15 07:08:01
Copyright © Kaluluosi All rights reserved
"""

import unittest
import os
import shutil
import tempfile
from contextlib import contextmanager
from typing import Literal
from gd_excelexporter.cli import cli
from click.testing import CliRunner


class GeneratorTest(unittest.TestCase):
    def setUp(self) -> None:
        self.runner = CliRunner()
        self.tmpdir = tempfile.TemporaryDirectory()
        self.cwd_backup = os.getcwd()
        os.chdir(self.tmpdir.name)  # 将工作目录切换到临时目录
        print("工作目录", os.getcwd())

    def tearDown(self) -> None:
        os.chdir(self.cwd_backup)
        self.tmpdir.cleanup()  # 清理临时目录

    @contextmanager
    def _init(
        self, generator: Literal["GDS1.0", "GDS2.0", "JSON2.0", "RESOURCE", "JSON1.0"]
    ):
        """
        测试项目初始化
        """
        res = self.runner.invoke(cli, ["init"], input=f"\n\n\n\n{generator}\n")

        self.assertFalse(res.exception)

        self.assertTrue(os.path.exists("settings"), "settings not exists")
        self.assertTrue(
            os.path.exists("settings/export.toml"), "export.toml not exists"
        )
        cwd_backup = os.getcwd()

        os.chdir("settings")
        shutil.copy("sample/示例.xlsx", "data/示例.xlsx")

        yield
        os.chdir(cwd_backup)

    def test_gen_gds1(self):
        """
        测试生成GDS1.0文件
        """

        with self._init("GDS1.0"):
            res = self.runner.invoke(cli, ["gen-all"])
            self.assertFalse(res.exception)
            self.assertTrue(os.path.exists("dist/示例/demo.gd"), "demo.gd not exists")
            self.assertTrue(
                os.path.exists("dist/settings.gd"), "settings.gd not exists"
            )

    def test_gen_gds2(self):
        """
        测试生成GDS2.0文件
        """

        with self._init("GDS2.0"):
            res = self.runner.invoke(cli, ["gen-all"])
            self.assertFalse(res.exception)
            self.assertTrue(os.path.exists("dist/示例/demo.gd"), "demo.gd not exists")
            self.assertTrue(
                os.path.exists("dist/settings.gd"), "settings.gd not exists"
            )

    def test_gen_json1(self):
        """
        测试生成JSON1.0文件
        """

        with self._init("JSON1.0"):
            res = self.runner.invoke(cli, ["gen-all"])
            self.assertFalse(res.exception)
            self.assertTrue(
                os.path.exists("dist/示例/demo.json"), "demo.json not exists"
            )
            self.assertTrue(
                os.path.exists("dist/settings.gd"), "settings.gd not exists"
            )

    def test_gen_json2(self):
        """
        测试生成JSON2.0文件
        """

        with self._init("JSON2.0"):
            res = self.runner.invoke(cli, ["gen-all"])
            self.assertFalse(res.exception)
            self.assertTrue(
                os.path.exists("dist/settings.gd"), "settings.gd not exists"
            )

    def test_gen_resource(self):
        """
        测试生成RESOURCE文件
        """

        with self._init("RESOURCE"):
            res = self.runner.invoke(cli, ["gen-all"])
            self.assertFalse(res.exception)
            self.assertTrue(
                os.path.exists("dist/settings.gd"), "settings.gd not exists"
            )

    def test_extract(self):
        with self._init("GDS2.0"):
            res = self.runner.invoke(cli, ["gen-all"])
            self.assertFalse(res.exception)
            self.assertTrue(os.path.exists("dist/示例/demo.gd"), "demo.gd not exists")
            self.assertTrue(
                os.path.exists("dist/settings.gd"), "settings.gd not exists"
            )

            res = self.runner.invoke(cli, ["extract"])

            self.assertFalse(res.exception)
            self.assertTrue(
                os.path.exists("lang/template.pot"), "template.pot not exists"
            )
