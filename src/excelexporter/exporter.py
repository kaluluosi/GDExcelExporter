import os
from turtle import width
import xlwings as xw
import glob

from typing import Sequence
from .logger import logger
from toml import load, dump


CFG = {
    "settings": {
        "ignore_sheet_mark": "~",  # 带星号的sheet不会导出
        "ignore_field_mark": "*",  # 字段忽略标志
        "custom_generator": "",  # 自定义加工脚本
        "completed_hook": "",  # 导表结束后调用脚本
        "custom_data_builder": "",  # 自定义data加工器
        "input": "data",  # 导入目录
        "output": "dist",  # 导出目录
        "project_root": "../",  # 导出到项目的路径，比如你的 output="../Godot项目/Scripts/Settings"，那么project_root="../Godot项目"
    }
}


def load_toml_config() -> dict:
    local_cfg_path = os.path.abspath("export.toml")
    if os.path.exists(local_cfg_path):
        cfg_data = load(local_cfg_path)
        CFG["settings"].update(cfg_data["settings"])
    else:
        logger.warning("没有配置文件，将使用内置默认配置")


def create_toml_config():
    with open("export.toml", "w+", newline="\n", encoding="utf-8") as f:
        dump(CFG, f)


def row2str_arr(row):
    return [str(cell.value) for cell in row]


def on_completed():
    """
    导表结束钩子
    """
    on_complete = CFG["settings"]["completed_hook"]
    if on_complete:
        with open(on_complete) as f:
            code = f.read()
            exec(code, globals(), {"CFG": CFG})
    else:
        completed_gd()


def excel2dict(workbook: xw.Book) -> dict:
    abspath: str = workbook.fullname
    abssource = os.path.abspath(CFG["settings"]["input"])
    absoutput = os.path.abspath(CFG["settings"]["output"])
    ignore_sheet_mark = CFG["settings"]["ignore_sheet_mark"]
    abspath_no_ext = os.path.splitext(abspath)[0]

    if not abspath.startswith(abssource):
        logger.error(f"{abspath} 不是配置表目录下的配置")
        return

    sheets: Sequence[xw.Sheet] = workbook.sheets

    # 过滤出不带*的表名
    sheets = filter(lambda sheet: not sheet.name.startswith(ignore_sheet_mark), sheets)

    custom_generator = CFG["settings"]["custom_generator"]
    if custom_generator:
        with open(custom_generator) as f:
            code = f.read()
        logger.info(f"使用 {custom_generator} 自定义导出")

    for sheet in sheets:
        if "-" in sheet.name:
            org_name, rename = sheet.name.split("-")
        else:
            org_name, rename = sheet.name, None

        data = {}
        row_values = sheet.range("A1").expand().raw_value
        data["define"] = {
            "type": row_values[0],
            "desc": row_values[1],
            "name": row_values[2],
        }
        data["table"] = list(row_values[3:])

        relative_path = os.path.join(
            abspath_no_ext.replace(abssource, ""), rename or org_name
        )
        output = absoutput + relative_path

        output_dirname = os.path.dirname(output)
        if not os.path.exists(output_dirname):
            os.makedirs(output_dirname)

        logger.info(f"导出: {abspath}:{sheet.name} => {output}")
        if custom_generator:
            exec(code, globals(), {"data": data, "output": output})
        else:
            gen_godot(data, output)

    workbook.close()


def gen_godot(data, output):
    import pprint
    import textwrap

    func_codes = []
    func_names = []

    def make_func(v, n, id):
        func_name = f"{n}_{id}"

        func_code = textwrap.dedent(
            f"""
static func {func_name}(args=[]):
{textwrap.indent(v, "    ")}
"""
        )
        func_codes.append(func_code)
        func_names.append(func_name)
        return func_name

    converter = {
        "": lambda v, n, id: v or 0,
        "string": lambda v, n, id: str(v) if v else "",
        "int": lambda v, n, id: int(str(v or 0).split(".")[0]),
        "float": lambda v, n, id: float(str(v or 0)),
        "bool": lambda v, n, id: v != "FALSE",
        "array": lambda v, n, id: eval(f'[{v.replace("|",",")}]') if v else [],
        "array_str": lambda v, n, id: ["%s" % e for e in v.split("|")] if v else [],
        "array_bool": lambda v, n, id: [e != "FALSE" for e in v.split("|")]
        if v
        else [],
        "dict": lambda v, n, id: eval(f'{{{v.replace("|",",")}}}') if v else {},
        "function": lambda v, n, id: make_func(v or "pass", n, id),
    }

    # 表格数据脚本模板
    template = """
    extends Reference
    class Function extends Reference:

        var func_name
        var script_path

        func _init(script_path, func_name):
            self.func_name = func_name
            self.script_path = script_path

        func call(args=[]):
            var this_script = load(script_path)
            return this_script.call(self.func_name, args)

    static func data():
        var None = null
        var False = false
        var True = true

        var data = \\
        {data}
        return data

    {funcs}
    """
    template = textwrap.dedent(template)

    # 在这里面写你的加工逻辑
    field_names = data["define"]["name"]
    field_types = data["define"]["type"]
    table = {}
    for row in data["table"]:

        id_type = field_types[0]
        id_cvt = converter[id_type] if id_type in converter else converter[""]
        id = id_cvt(row[0], None, None)

        row_data = {}
        for index, value in enumerate(row):
            field_name: str = field_names[index]
            field_type = field_types[index]
            if field_name.startswith(CFG["settings"]["ignore_field_mark"]):
                continue
            cvt = converter[field_type] if field_type in converter else converter[""]
            row_data[field_name] = cvt(value, field_name, id)
        table[row_data["id"]] = row_data  # 我们规定第一个字段是ID字段

    funcs = textwrap.dedent("\n".join(func_codes))

    code = template.format(
        data=pprint.pformat(table, indent=2, width=10000000), funcs=funcs
    )

    project_root = CFG["settings"]["project_root"]
    relpath = os.path.relpath(output, project_root).replace("\\", "/")
    code = textwrap.dedent(code)

    for func_name in func_names:
        code = code.replace(
            f"'{func_name}'", f"Function.new('res://{relpath}.gd','{func_name}')"
        )

    with open(output + ".gd", "w+", newline="\n", encoding="utf-8") as f:
        f.write(code)


def completed_gd():
    from glob import glob
    import os
    import textwrap

    output_path = CFG["settings"]["output"]
    settings_file_path = os.path.join(output_path, "Settings.gd")
    project_root = CFG["settings"]["project_root"]

    lines = []

    for path in glob(f"{output_path}/**/*.*", recursive=True):
        if path == settings_file_path:
            logger.info("跳过 Settings.gd")
            continue
        basename = os.path.basename(path)
        setting_name = os.path.splitext(basename)[0]
        relpath = os.path.relpath(path, project_root).replace("\\", "/")
        lines.append(f"var {setting_name} = load('res://{relpath}')")

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

    with open(settings_file_path, "w", newline="\n", encoding="utf-8") as f:
        f.write(code)


def gen_all(cwd: str = "."):
    os.chdir(cwd)
    load_toml_config()
    abssource = os.path.abspath(CFG["settings"]["input"])
    with xw.App(visible=False) as app:
        exts = [".xlsx", ".xls"]
        for ext in exts:
            full_paths = glob.glob(f"{abssource}/**/*{ext}", recursive=True)
            for full_path in full_paths:
                filename = os.path.basename(full_path)
                if filename.startswith("~$"):
                    logger.warning(f"{filename} 不是配置表，跳过！")
                    continue
                book = app.books.open(full_path)
                excel2dict(book)
        on_completed()


def gen_one(path, cwd: str = "."):
    with xw.App(visible=False) as app:
        book = app.books.open(path)
        excel2dict(book)
        on_completed()
