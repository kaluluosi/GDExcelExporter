"""
author:        kaluluosi111 <kaluluosi@gmail.com>
date:          2024-04-15 14:55:03
Copyright © Kaluluosi All rights reserved
"""

import abc
from contextlib import contextmanager
import glob
import logging
import os
from typing import Optional

from gd_excelexporter.base.generator import Table
from gd_excelexporter.exceptions import IllegalFile, IllegalGenerator
from gd_excelexporter.config import Configuration
from gd_excelexporter.base import Generator
from gd_excelexporter.utils import discover_generator
from gd_excelexporter.converter import Converter

logger = logging.getLogger(__name__)


class Engine(abc.ABC):
    # 配置表抽取出来的多语言文本
    LANG_FILE = "lang/.settings"

    def __init__(self, config: Configuration) -> None:
        self.config = config
        self.generator: Optional[Generator] = self._get_generator()

        # 本地化字符串，搜集所有配置表的本地化字符串
        # 需要在 _excel2dict里面实现将多语言字段只添加进去
        self.localized_strs = set()
        # 类型转换器
        self.cvt = Converter()

    def _get_generator(self) -> Generator:
        """
         根据toml配置获取导出器

        Raises:
            IllegalGenerator: 不合法导出器异常

        Raises:
            IllegalGenerator: _description_

        Returns:
           Generator: 导出器
        """
        generators = discover_generator()

        if self.config.custom_generator in generators.names:
            module = generators[self.config.custom_generator].load()
            logger.info(
                f"使用插件导出器 {self.config.custom_generator} :{module.__name__}"
            )  # noqa
        else:
            raise IllegalGenerator(self.config.custom_generator, generators.names)

        return module()

    @abc.abstractmethod
    def _excel2dict(self, excel_filename: str) -> "dict[str, Table]":
        """
        将excel转成字典。
        需要具体实现，因为Mac不支持xlwings，需要用xlrd等别的实现

        Args:
            excel_file (str): excel文件路径

        Returns:
            dict[str, Table]: 返回sheet名->Table的字典
        """
        pass

    def _generate(self, excel_filename: str):
        # excel文件绝对路径
        excel_abs_path: str = os.path.abspath(excel_filename)

        # 输入目录的绝对路径
        abs_input_path = os.path.abspath(self.config.input)
        # 暑促目录的绝对路径
        abs_output_path = os.path.abspath(self.config.output)

        # excel文件路径（无扩展名）
        excel_abs_path_without_ext: str = os.path.splitext(excel_abs_path)[0]

        if self.generator is None:
            raise RuntimeError("没有加载任何导出器！")

        if not excel_abs_path.startswith(abs_input_path):
            # 如果输入目录不是输入文件所在目录，则抛出异常
            raise IllegalFile(excel_abs_path, abs_input_path)

        sheet_tables = self._excel2dict(excel_abs_path)

        for sheet_name, table in sheet_tables.items():
            try:
                if "-" in sheet_name:
                    org_name, rename = sheet_name.split("-")
                else:
                    org_name, rename = sheet_name, None

                relative_path = os.path.join(
                    excel_abs_path_without_ext.replace(abs_input_path, ""),
                    rename or org_name,
                )
                output = abs_output_path + relative_path

                output_dirname = os.path.dirname(output)
                # 保持输出的文件目录层级结构与输入一致
                if not os.path.exists(output_dirname):
                    os.makedirs(output_dirname)

                code = self.generator.generate(table, self.config)

                # code = "# 本文件由代码生成，不要手动修改\n"+code
                output = f"{output}.{self.generator.__extension__}"
                with open(output, "w", encoding="utf-8", newline="\n") as f:
                    f.write(code)
                    logger.info(f"导出：{excel_abs_path}:{sheet_name} => {output}")
            except Exception:
                logger.error(f"{sheet_name} 导出失败", exc_info=True)

    def _save_lang_file(self, filename: str):
        with open(filename, "w", encoding="utf-8", newline="\n") as f:
            f.write("## 这是用于抽取代码中多语言的辅助文件，用来辅助生成POT用的\n")
            f.write("func localization():\n")
            lines = []
            for txt in self.localized_strs:
                if txt:
                    lines.append(f"  tr('{txt}')\n")
                    # logger.info(f"抽出 {txt}")

            f.writelines(lines)

    def gen_one(self, excel_filename: str):
        self._generate(excel_filename)
        if self.generator:
            self.generator.completed_hook(self.config)

    def gen_all(self):
        abs_input_path = os.path.abspath(self.config.input)
        exts = [".xlsx", ".xls"]
        for ext in exts:
            full_paths = glob.glob(f"{abs_input_path}/**/*{ext}", recursive=True)
            for full_path in full_paths:
                filename = os.path.basename(full_path)
                if filename.startswith("~$"):
                    logger.warning(f"{filename} 不是配置表，跳过！")
                    continue
                self._generate(full_path)

        if self.generator:
            self.generator.completed_hook(self.config)

    @contextmanager
    def extract_lang(self):
        """
        将配置表中的多语言字符串抽取出来，生成gd文件，用于提取。

        配置表中的多语言字段要能够供Godot babel或者Babel提取需要先抽取到一个gd脚本。
        这个函数就是用来生成这个gd脚本。当生成POT文件后就删除。

        通过`with`来包裹让其使用完后自动清理。

        ```
        with engine.extract_lang():
            ...
        ```
        """
        abs_input = os.path.abspath(self.config.input)
        exts = [".xlsx", ".xls"]
        for ext in exts:
            full_paths = glob.glob(f"{abs_input}/**/*{ext}", recursive=True)
            for full_path in full_paths:
                filename = os.path.basename(full_path)
                if filename.startswith("~$"):
                    logger.warning(f"{filename} 不是配置表，跳过！")
                    continue
                self._excel2dict(full_path)  # 直接读所有表，不做转换抽取翻译字符
                logger.info(f"抽出多语言: {full_path}")
        self._save_lang_file(self.LANG_FILE)
        logger.info(f"生成配置语言辅助文件(跳过空字符): {self.LANG_FILE}")
        yield
        os.remove(self.LANG_FILE)
