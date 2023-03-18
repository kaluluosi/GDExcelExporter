import glob
import os
import pprint
import logging
import textwrap
from excelexporter.config import Configuration
from excelexporter.sheetdata import SheetData
from excelexporter.generator import Converter, Type

# 导出格式
extension = "gd"

logger = logging.getLogger(__name__)

func_names = []
func_codes = []

cvt = Converter()

cvt.register(Type.STRING, lambda v, n, id, p: str(v) if v else "")
cvt.register(
    Type.INT, lambda v, n, id, p: int(str(v or 0).split(".")[0])
)
cvt.register(Type.FLOAT, lambda v, n, id, p: float(str(v or 0)))
cvt.register(Type.BOOL, lambda v, n, id, p: v != "FALSE")
cvt.register(
    Type.ARRAY,
    lambda v, n, id, p: eval(f'[{v.replace("|",",")}]') if v else []
)
cvt.register(
    Type.ARRAY_STR,
    lambda v, n, id, p: ["%s" %
                         e for e in v.split("|")]if v else []
)
cvt.register(
    Type.ARRAY_BOOL,
    lambda v, n, id, p: [e != "FALSE" for e in v.split("|")] if v else []
)
cvt.register(
    Type.DICT,
    lambda v, n, id, p: eval(f'{{{v.replace("|",",")}}}')
    if v else {}
)
cvt.register(
    Type.FUNCTION,
    lambda v, n, id, p: make_func(v or "pass", n, id, p)
)


def make_func(v, fn, id, p):
    func_name = f"{fn}_{id}"

    params = "(args=[])" if not p else p

    func_code = textwrap.dedent(
        f"""
static func {func_name}{params}:
{textwrap.indent(v, "    ")}
"""
    )
    func_names.append(func_name)
    func_codes.append(func_code)
    return func_name


def generator(sheetdata: SheetData, config: Configuration):
    # 表格数据脚本模板
    template = """
    extends Reference
    var None = null
    var False = false
    var True = true

    var data = \\
    {data}

    {funcs}
    """
    template = textwrap.dedent(template)
    field_names = sheetdata.define.name
    field_types = sheetdata.define.type
    table = {}

    for row in sheetdata.table:
        id_type = field_types[0]
        id = cvt(id_type, row[0], None, None)

        row_data = {}

        for index, value in enumerate(row):
            field_name: str = field_names[index]
            field_type = field_types[index]
            row_data[field_name] = cvt(field_type, value, field_name, id)

        table[row_data["id"]] = row_data

    funcs = textwrap.dedent("\n".join(func_codes))

    code = template.format(
        data=pprint.pformat(table, indent=2, width=1000000000,
                            compact=True, sort_dicts=True),
        funcs=funcs
    )

    code = textwrap.dedent(code)

    for func_name in func_names:
        code = code.replace(
            f"'{func_name}'",
            f"funcref(self,'{func_name}')"
        )

    return code


def completed_hook(config: Configuration):

    output = config.output
    settings_file_path = os.path.join(output, "settings.gd")
    project_root = config.project_root

    lines = []

    for path in glob.glob(f"{output}/**/*.*", recursive=True):
        if path == settings_file_path:
            continue  # 跳过 settings.gd
        basename = os.path.basename(path)
        setting_name = os.path.splitext(basename)[0]
        relpath = os.path.relpath(path, project_root).replace("\\", "/")
        lines.append(f"var {setting_name} = load('res://{relpath}').new()")

        # 去掉缩进
    code = textwrap.dedent(
        """
    extends Node
    # 这个脚本你需要挂到游戏的Autoload才能全局读表

    {refs_code}
    """
    )
    refs_code = "\n".join(lines)

    code = code.format(refs_code=refs_code)

    with open(settings_file_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(code)
        logger.info("创建setting.gd")
