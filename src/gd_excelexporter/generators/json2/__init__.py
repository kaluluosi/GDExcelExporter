import glob
import json
import os
import logging
import textwrap
from gd_excelexporter.config import Configuration
from gd_excelexporter.core.generator import Generator, Table

logger = logging.getLogger(__name__)


class JSON2Generator(Generator):
    # 导出格式
    __extension__ = "json"

    def generate(self, table: Table, config: Configuration):
        # 表格数据脚本模板

        # 由于json不支持int做key，所以这里需要转换一下
        new_table = {}
        for id, row in table.items():
            row_data = {}

            for field, var in row.items():
                field_name: str = field
                row_data[field_name] = var.value

            new_table[id] = row_data

        code = json.dumps(new_table, ensure_ascii=False, indent=2)

        return code

    def completed_hook(self, config: Configuration):
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
            logger.info(f"创建：{settings_file_path}")
