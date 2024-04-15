import glob
import os
import logging
import jinja2
import pkg_resources

from gd_excelexporter.base.generator import Generator, Table
from gd_excelexporter.config import Configuration
from gd_excelexporter.converter import Variant
from gd_excelexporter.converter import Type

# jinja2 docs: http://doc.yonyoucloud.com/doc/jinja2-docs-cn/templates.html#id2

logger = logging.getLogger(__name__)


class GDS2Generator(Generator):
    # 导出格式
    __extension__ = "gd"

    def __init__(self) -> None:
        self.loader = jinja2.FileSystemLoader(
            pkg_resources.resource_filename(__package__, "")  # type: ignore
        )
        self.env = jinja2.Environment(autoescape=False, loader=self.loader)
        self.env.filters["cvt"] = self.converter

    def converter(self, var: Variant):
        type_define = var.type_define
        if type_define.type_name == Type.STRING:
            value = var.value.replace("\n", "\\n")
            return f"'{value}'"

        if type_define.type_name == Type.FUNCTION:
            func_name = f"{var.field_name}_{var.id}"
            return f"Callable(self,'{func_name}')"

        return var.value

    def generate(self, table: Table, config: Configuration):
        # 表格数据脚本模板
        template = self.env.get_template("data_template.gd")
        code = template.render(table=table)
        return code

    def completed_hook(self, config: Configuration):
        output = config.output
        settings_file_path = os.path.join(output, "settings.gd")
        project_root = config.project_root

        lines = []

        for path in glob.glob(f"{output}/**/*.{self.__extension__}", recursive=True):
            if path == settings_file_path:
                continue  # 跳过 settings.gd
            basename = os.path.basename(path)
            setting_name = os.path.splitext(basename)[0]
            relpath = os.path.relpath(path, project_root).replace("\\", "/")
            lines.append(f"var {setting_name} = load('res://{relpath}').new()")

        template = self.env.get_template("setting_template.gd")
        code = template.render(lines=lines)

        with open(settings_file_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(code)
            logger.info(f"创建：{settings_file_path}")
