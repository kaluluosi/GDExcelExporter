"""
author:        kaluluosi111 <kaluluosi@gmail.com>
date:          2024-04-15 07:08:01
Copyright © Kaluluosi All rights reserved
"""

import unittest
import os
import shutil
import tempfile
from excelexporter.cli import main
from click.testing import CliRunner


class TestCli(unittest.TestCase):
    def setUp(self) -> None:
        self.runner = CliRunner()
        self.tmpdir = tempfile.TemporaryDirectory()
        self.cwd_backup = os.getcwd()
        os.chdir(self.tmpdir.name)  # 将工作目录切换到临时目录

    def tearDown(self) -> None:
        os.chdir(self.cwd_backup)
        self.tmpdir.cleanup()  # 清理临时目录

    def test_init(self):
        """
        测试项目初始化
        """
        res = self.runner.invoke(main, ["init"], input="\n\n\n\n")

        self.assertFalse(res.exception)

        self.assertTrue(os.path.exists("settings"), "settings not exists")
        self.assertTrue(
            os.path.exists("settings/export.toml"), "export.toml not exists"
        )

    def test_gen_all(self):
        """
        测试生成所有文件
        """
        self.test_init()
        os.chdir("settings")
        shutil.copy("sample/示例.xlsx", "data/示例.xlsx")
        res = self.runner.invoke(main, ["gen-all"])
        if res.exception:
            self.fail(res.exception.with_traceback(None))

        self.assertTrue(os.path.exists("dist/示例/demo.gd"), "demo.gd not exists")

    def test_extract(self):
        """
        测试提取多语言
        """
        self.test_init()
        os.chdir("settings")
        shutil.copy("sample/示例.xlsx", "data/示例.xlsx")
        self.test_gen_all()
        res = self.runner.invoke(main, ["extract"])
        if res.exception:
            self.fail(res.exception.with_traceback(None))

        self.assertTrue(os.path.exists("lang/template.pot"), "template.pot not exists")
