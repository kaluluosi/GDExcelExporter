import glob
import os
import logging
import jinja2
import pkg_resources
from excelexporter.config import Configuration
from excelexporter.sheetdata import SheetData
from excelexporter.generator import Variant
from excelexporter.generator import Type

# jinja2 docs: http://doc.yonyoucloud.com/doc/jinja2-docs-cn/templates.html#id2

logger = logging.getLogger(__name__)

# 导出格式
extension = "gd"

loader = jinja2.FileSystemLoader(
    pkg_resources.resource_filename(__package__, ""))
env = jinja2.Environment(autoescape=False, loader=loader)


def converter(var: Variant):
    type_define = var.type_define
    if type_define.type_name == Type.STRING:
        value = var.value.replace("\n", "\\n")
        return f"'{value}'"

    if type_define.type_name == Type.FUNCTION:
        func_name = f"{var.field_name}_{var.id}"
        return f"funcref(self,'{func_name}')"

    return var.value


env.filters["cvt"] = converter


def generator(sheetdata: SheetData, config: Configuration):
    # 表格数据脚本模板
    template = env.get_template("data_template.gd")
    code = template.render(sheetdata=sheetdata)
    return code


def completed_hook(config: Configuration):
    output = config.output
    settings_file_path = os.path.join(output, "settings.gd")
    project_root = config.project_root

    lines = []

    for path in glob.glob(f"{output}/**/*.{extension}", recursive=True):
        if path == settings_file_path:
            continue  # 跳过 settings.gd
        basename = os.path.basename(path)
        setting_name = os.path.splitext(basename)[0]
        relpath = os.path.relpath(path, project_root).replace("\\", "/")
        lines.append(f"var {setting_name} = load('res://{relpath}').new()")

    template = env.get_template("setting_template.gd")
    code = template.render(lines=lines)

    with open(settings_file_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(code)
        logger.info("创建setting.gd")
