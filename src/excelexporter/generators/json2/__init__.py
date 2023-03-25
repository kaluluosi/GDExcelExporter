import glob
import json
import os
import logging
import textwrap
from excelexporter.config import Configuration
from excelexporter.sheetdata import SheetData


# 导出格式
extension = "json"

logger = logging.getLogger(__name__)


EE_DATATABLE_CLASS = """
class_name EEDataTable
extends Resource

@export
var data = {}
"""


def generator(sheetdata: SheetData, config: Configuration):
    # 表格数据脚本模板

    table = {}

    for id, row in sheetdata.items():
        row_data = {}

        for field, var in row.items():
            field_name: str = field
            row_data[field_name] = var.value

        table[id] = row_data

    code = json.dumps(table, ensure_ascii=False, indent=2)

    return code


def completed_hook(config: Configuration):

    output = config.output
    settings_file_path = os.path.join(output, "settings.gd")
    project_root = config.project_root

    lines = []

    loader = textwrap.dedent("""
    static func loader(path:String):
        var file = FileAccess.open(path,FileAccess.READ)
        var txt = file.get_as_text()
        var data = JSON.parse_string(txt)
        file.close()
        return data
    """)

    for path in glob.glob(f"{output}/**/*.json", recursive=True):
        if path == settings_file_path:
            continue  # 跳过 settings.gd
        basename = os.path.basename(path)
        setting_name = os.path.splitext(basename)[0]
        relpath = os.path.relpath(path, project_root).replace("\\", "/")
        lines.append(f"var {setting_name} = loader('res://{relpath}')")

        # 去掉缩进
    code = textwrap.dedent(
        """
    extends Node
    # 这个脚本你需要挂到游戏的Autoload才能全局读表

    {loader}
    {refs_code}
    """
    )
    refs_code = "\n".join(lines)

    code = code.format(loader=loader, refs_code=refs_code)

    with open(settings_file_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(code)
        logger.info("创建setting.gd")
