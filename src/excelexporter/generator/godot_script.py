import glob
import os
import pprint
import textwrap

func_names = []
func_codes = []

CONVERTER = {
    "": lambda v, n, id: v or 0,
    "string": lambda v, n, id: str(v) if v else "",
    "int": lambda v, n, id: int(str(v or 0).split(".")[0]),
    "float": lambda v, n, id: float(str(v or 0)),
    "bool": lambda v, n, id: v != "FALSE",
    "array": lambda v, n, id: eval(f'[{v.replace("|",",")}]') if v else [],
    "array_str": lambda v, n, id: ["%s" % e for e in v.split("|")]
    if v else [],
    "array_bool": lambda v, n, id: [e != "FALSE" for e in v.split("|")]
    if v
    else [],
    "dict": lambda v, n, id: eval(f'{{{v.replace("|",",")}}}')
    if v else {},
    "function": lambda v, n, id: make_func(v or "pass", n, id),
}


def make_func(v, n, id):
    func_name = f"{n}_{id}"

    func_code = textwrap.dedent(
        f"""
static func {func_name}(args=[]):
{textwrap.indent(v, "    ")}
"""
    )
    func_names.append(func_name)
    func_codes.append(func_code)
    return func_name


def generator(data: dict, CFG: dict):

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

    # 在这里面写你的加工逻辑
    field_names = data["define"]["name"]
    field_types = data["define"]["type"]
    table = {}
    for row in data["table"]:

        id_type = field_types[0]
        id_cvt = CONVERTER[id_type] if id_type in CONVERTER else CONVERTER[""]
        id = id_cvt(row[0], None, None)

        row_data = {}
        for index, value in enumerate(row):
            field_name: str = field_names[index]
            field_type = field_types[index]
            if field_name.startswith(CFG["settings"]["ignore_field_mark"]):
                continue

            if field_type in CONVERTER:
                cvt = CONVERTER[field_type]
            else:
                cvt = CONVERTER[""]

            row_data[field_name] = cvt(value, field_name, id)
        table[row_data["id"]] = row_data  # 我们规定第一个字段是ID字段

    funcs = textwrap.dedent("\n".join(func_codes))

    code = template.format(
        data=pprint.pformat(table, indent=2, width=10000000), funcs=funcs
    )

    code = textwrap.dedent(code)

    for func_name in func_names:
        code = code.replace(
            f"'{func_name}'",
            f"funcref(self,'{func_name}')"
        )

    return code, "gd"


def completed(CFG: dict):

    output_path = CFG["settings"]["output"]
    settings_file_path = os.path.join(output_path, "settings.gd")
    project_root = CFG["settings"]["project_root"]

    lines = []

    for path in glob.glob(f"{output_path}/**/*.*", recursive=True):
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

    return code
