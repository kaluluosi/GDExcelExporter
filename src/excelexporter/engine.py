import glob
import os
import sys
import xlwings as xw
import logging
from excelexporter.config import Configuration
from excelexporter.generator import Converter, Generator, CompletedHook, Variant  # noqa
from excelexporter.sheetdata import SheetData, TypeDefine
from typing import Dict, Optional

if sys.version_info < (3, 10):
    from importlib_metadata import entry_points
else:
    from importlib.metadata import entry_points

# 导表工具引擎

logger = logging.getLogger(__name__)


class IllegalFile(Exception):

    def __init__(self, filename: str, *args: object) -> None:
        super().__init__(f"{filename} 不是配置表目录下的配置", *args)


class IllegalGenerator(Exception):
    def __init__(self, name: str, *args: object) -> None:
        super().__init__(
            name,
            *args
        )


def discover_generator():
    generators = entry_points(
        group="excelexporter.generator")
    return generators


class Engine(xw.App):

    def __init__(self, config: Configuration) -> None:
        super().__init__(visible=False)
        self.config = config
        self.generator: Optional[Generator] = None
        self.completed_hook: Optional[CompletedHook] = None
        self.extension: str = ""

        self.localized_strs = set()
        self.cvt = Converter()

        self.init_generator()

    def init_generator(self):

        generator = None
        completed_hook = None
        extension = None

        # 如果有自定义导出器就优先用自定义导出器
        if self.config.custom_generator.endswith(".py"):
            with open(self.config.custom_generator) as f:
                code = f.read()
                exec(code)
                self.generator = generator
                self.completed_hook = completed_hook
                self.extension = extension

                if (generator and completed_hook and extension) is False:
                    raise IllegalGenerator(
                        self.config.custom_generator,
                        "自定义导出器不完整，generator、completed_hook、extension存在没定义。")

                logger.info(f"使用 {self.config.custom_generator} 自定义导出器")
        else:
            # 找出插件
            generators = discover_generator()

            if self.config.custom_generator in generators.names:
                module = generators[self.config.custom_generator].load()
                logger.info(
                    f"使用插件导出器 {self.config.custom_generator} :{module.__name__}")  # noqa
            else:
                raise IllegalGenerator(
                    self.config.custom_generator, generators.names)

            self.generator = getattr(module, "generator")
            self.completed_hook = getattr(module, "completed_hook")
            self.extension = getattr(module, "extension")

    def _gen(self, excel_file: str):
        wb_abs_path: str = os.path.abspath(excel_file)
        abs_input_path: str = os.path.abspath(self.config.input)
        abs_output_path: str = os.path.abspath(self.config.output)
        wb_abs_path_without_ext: str = os.path.splitext(wb_abs_path)[0]

        if not wb_abs_path.startswith(abs_input_path):
            raise IllegalFile(wb_abs_path, abs_input_path)

        sheet_datas = self._excel2dict(wb_abs_path)

        for sheet_name, sheetdata in sheet_datas.items():
            try:
                if "-" in sheet_name:
                    org_name, rename = sheet_name.split("-")
                else:
                    org_name, rename = sheet_name, None

                relative_path = os.path.join(
                    wb_abs_path_without_ext.replace(abs_input_path, ""),
                    rename or org_name
                )
                output = abs_output_path + relative_path

                output_dirname = os.path.dirname(output)
                # 保持输出的文件目录层级结构与输入一致
                if not os.path.exists(output_dirname):
                    os.makedirs(output_dirname)

                code = self.generator(sheetdata, self.config)

                # code = "# 本文件由代码生成，不要手动修改\n"+code
                output = f"{output}.{self.extension}"
                with open(output, "w", encoding="utf-8", newline="\n") as f:
                    f.write(code)
                    logger.info(f"导出：{wb_abs_path}:{sheet_name} => {output}")
            except Exception:
                logger.error(f"{sheet_name} 导出失败", exc_info=True)

    def _excel2dict(self, wb_file: str) -> Dict[str, SheetData]:
        """
        workbook解析加工成字典
        """
        with self.books.open(wb_file) as book:
            ignore_sheet_mark = self.config.ignore_sheet_mark
            # 过滤掉打了忽略标志的sheet
            sheets = filter(
                lambda sheet: not sheet.name.startswith(ignore_sheet_mark),
                book.sheets
            )

            wb_data = {}

            # 先讲sheet转sheet_data
            for sheet in sheets:
                sheet_data = SheetData()
                row_values = sheet.range("A1").expand().raw_value

                sheet_data.define.type = list(row_values[0])
                sheet_data.define.desc = list(row_values[1])
                sheet_data.define.name = list(row_values[2])

                sheet_data.table = list([list(row) for row in row_values[3:]])
                # 找出所有被打了忽略标记的字段
                for col, field in enumerate(sheet_data.define.name):
                    # 跳过没命令的字段

                    if field is None or field.startswith(self.config.ignore_field_mark):  # noqa
                        del sheet_data.define.type[col]
                        del sheet_data.define.desc[col]
                        del sheet_data.define.name[col]
                        for row in sheet_data.table:
                            del row[col]

                wb_data[sheet.name] = sheet_data

            cvt = Converter()
            for sheet_name, sheet_data in wb_data.items():
                field_names = sheet_data.define.name
                field_types = sheet_data.define.type
                table = {}

                for row in sheet_data.table:
                    id_type = TypeDefine.from_str(field_types[0])
                    id_name = field_names[0]
                    id_value = row[0]
                    id = cvt(id_value, id_type, id_name, id_value)

                    row_data = {}

                    for index, value in enumerate(row):
                        field_name: str = field_names[index]
                        field_type = TypeDefine.from_str(field_types[index])
                        variant: Variant = cvt(
                            id.value, field_type, field_name, value
                        )
                        row_data[field_name] = variant
                        self.localized_strs = self.localized_strs.union(
                            variant.local_strs())

                    table[id.value] = row_data
                wb_data[sheet_name] = table

            return wb_data

    def save_lang_file(self):

        with open("language.gd", "w", encoding="utf-8", newline="\n") as f:
            f.write("func localization():\n")
            lines = []
            for txt in self.localized_strs:
                lines.append(
                    f"  tr('{txt}')\n"
                )
            f.writelines(lines)

    def gen_one(self, filename: str):
        self._gen(filename)
        if self.completed_hook:
            self.completed_hook(self.config)

    def gen_all(self):
        abs_input = os.path.abspath(self.config.input)
        exts = [".xlsx", ".xls"]
        for ext in exts:
            full_paths = glob.glob(f"{abs_input}/**/*{ext}", recursive=True)
            for full_path in full_paths:
                filename = os.path.basename(full_path)
                if filename.startswith("~$"):
                    logger.warning(f"{filename} 不是配置表，跳过！")
                    continue
                self._gen(full_path)

        if self.completed_hook:
            self.completed_hook(self.config)

    def extract_pot(self):
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
                logger.info(f"导出语言表: {full_path}")
        self.save_lang_file()
