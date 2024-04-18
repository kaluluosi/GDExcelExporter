"""
author:        kaluluosi111 <kaluluosi@gmail.com>
date:          2024-04-15 14:55:03
Copyright © Kaluluosi All rights reserved
"""

import abc
import glob
import logging
import os
import sys
from typing import Type

from gd_excelexporter.core.models import (
    Table,
    TableMap,
    RawTableMap,
)
from gd_excelexporter.core.models import Variant
from gd_excelexporter.exceptions import IllegalFile
from gd_excelexporter.config import Configuration
from gd_excelexporter.core.generator import Generator
from gd_excelexporter.core.type_define import TrTypeDefine, TypeDefine

from babel.messages.frontend import CommandLineInterface

if sys.version_info < (3, 10):
    from importlib_metadata import entry_points
else:
    from importlib.metadata import entry_points


logger = logging.getLogger(__name__)


class Engine(abc.ABC):
    # 配置表抽取出来的多语言文本
    LANG_FILE = "lang/.settings"

    def __init__(self, config: Configuration) -> None:
        self.config = config

    def _excel2tablemap(self, excel_filename: str) -> TableMap:
        """
        将excel转成table map。

        Args:
            excel_file (str): excel文件路径

        Returns:
            dict[str, Table]: 返回sheet名->Table的字典
        """
        rawtablemap = self._excel2rawtablemap(excel_filename)

        tablemap: TableMap = {}

        for sheet_name, rawtable in rawtablemap.items():
            # 如果sheet名以ignore_sheet_mark开头就跳过
            # NOTE: 在这里做sheet的忽略
            if sheet_name.startswith(self.config.ignore_sheet_mark):
                continue

            table: Table = {}
            # 先遍历构抽取头三行字段定义define
            field_types = rawtable[0]
            field_names = rawtable[2]

            for row in rawtable[3:]:
                id_type: TypeDefine = TypeDefine.from_str(field_types[0])
                id_value = id_type.convert(row[0])

                row_data = {}
                for index, value in enumerate(row):
                    field_name: str = field_names[index]

                    # field_name 可能是空字符或者None，这时跳过
                    if not field_name:
                        continue

                    # 如果字段名以ignore_field_mark开头就跳过
                    # NOTE: 在这里做字段的忽略
                    if field_name.startswith(self.config.ignore_field_mark):
                        continue

                    type_define: TypeDefine = TypeDefine.from_str(field_types[index])
                    variant: Variant = Variant(
                        type_define=type_define,
                        field_name=field_name,
                        value=type_define.convert(value),
                        id=id_value,
                    )
                    row_data[field_name] = variant

                table[id_value] = row_data

            tablemap[sheet_name] = table

        return tablemap

    @abc.abstractmethod
    def _excel2rawtablemap(self, excel_filename: str) -> RawTableMap:
        """
        将sheet转换成原始字典数据

        本方法需要具体的Engine实现去实现

        以行号为key，行数组list为value。
        """
        pass

    def _generate(self, excel_filename: str):
        # excel文件绝对路径
        excel_abs_path: str = os.path.abspath(excel_filename)

        # 输入目录的绝对路径
        abs_input_path = os.path.abspath(self.config.input)
        # 输出目录的绝对路径
        abs_output_path = os.path.abspath(self.config.output)

        # excel文件路径（无扩展名）
        excel_abs_path_without_ext: str = os.path.splitext(excel_abs_path)[0]

        generator = Generator.get_generator(self.config.custom_generator)

        if generator is None:
            raise RuntimeError("没有加载任何导出器！")

        if not excel_abs_path.startswith(abs_input_path):
            # 如果输入目录不是输入文件所在目录，则抛出异常
            raise IllegalFile(excel_abs_path, abs_input_path)

        tablemap = self._excel2tablemap(excel_abs_path)

        for sheet_name, table in tablemap.items():
            try:
                # 处理sheet名与导出文件名
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

                code = generator.generate(table, self.config)

                output = f"{output}.{generator.__extension__}"
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
            for txt in TrTypeDefine.__tr_strs__:
                if txt:
                    lines.append(f"  tr('{txt}')\n")
                    # logger.info(f"抽出 {txt}")

            f.writelines(lines)

    def gen_one(self, excel_filename: str):
        self._generate(excel_filename)
        generator = Generator.get_generator(self.config.custom_generator)
        generator.completed_hook(self.config)

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

        generator = Generator.get_generator(self.config.custom_generator)
        generator.completed_hook(self.config)

    def extract_pot(self):
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
                self._excel2tablemap(full_path)  # 直接读所有表，抽取翻译字符
                logger.info(f"抽出多语言: {full_path}")
        self._save_lang_file(self.LANG_FILE)
        logger.info(f"生成配置语言辅助文件(跳过空字符): {self.LANG_FILE}")

        babel_keywords = self.config.localization.babel_keywords
        pot_file = self.config.localization.pot_file

        keyword_args = [f"-k {kw} " for kw in babel_keywords]

        cfg_file = os.path.abspath("babel.cfg")

        CommandLineInterface().run(  # noqa
            [
                "pybabel",
                "extract",
                "-F",
                cfg_file,
                *keyword_args,
                "-o",
                pot_file,
                self.config.project_root,
            ]
        )

        logger.info("生成POT文件: %s" % pot_file)

        os.remove(self.LANG_FILE)

    @staticmethod
    def register_engines():
        engines = entry_points(group="gd_excelexporter.engine")
        return engines

    @staticmethod
    def get_engine_cls(name: str) -> Type["Engine"]:
        engines = entry_points(group="gd_excelexporter.engine")
        if name in engines.names:
            engine_cls = engines[name].load()
            return engine_cls  # type: ignore
        else:
            raise RuntimeError(f"没有找到名为 {name} 的引擎！")

    @classmethod
    def create_engine(cls, name: str, config: Configuration):
        return cls.get_engine_cls(name)(config)
