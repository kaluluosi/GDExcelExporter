from distutils.log import info
from distutils.sysconfig import customize_compiler
import os
import json
import hashlib
import xlwings as xw
import glob

from typing import Sequence

from .logger import logger
from toml import load, dump


CFG = {
    "settings":{
        "ignore_sheet_mark": "*",  # 带星号的sheet不会导出
        "custom_generator": "", # 自定义加工脚本,
        "completed_hook": "", # 导表结束后调用脚本
        "input": "data", # 导入目录
        "output":"dist", # 导出目录
        "project_root":"../" # 导出到项目的路径，比如你的 output="../Godot项目/Scripts/Settings"，那么project_root="../Godot项目"
    }
}

MD5MAP = {}

def get_md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def load_md5map():
    local_md5map = os.path.abspath("md5.txt")
    if os.path.exists(local_md5map):
        with open("md5.txt",'r') as f:
            MD5MAP = json.load(f)

def save_md5map():
    local_md5map = os.path.abspath("md5.txt")
    with open(local_md5map, 'w+', encoding='utf-8') as f:
        json.dump(MD5MAP, f, ensure_ascii=False, indent=4)

def load_toml_config() -> dict:
    local_cfg_path = os.path.abspath("export.toml")
    if os.path.exists(local_cfg_path):
        cfg_data = load(local_cfg_path)
        CFG.update(cfg_data)
    else:
        logger.warning("没有配置文件，将使用内置默认配置")

def create_toml_config():
    with open("export.toml", 'w+') as f:
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
            exec(code, globals(), {"CFG":CFG})
    else:
        completed_gd()

def excel2dict(workbook:xw.Book) -> dict:
    abspath:str = workbook.fullname
    abssource = os.path.abspath(CFG["settings"]["input"])
    absoutput = os.path.abspath(CFG["settings"]["output"])
    ignore_sheet_mark = CFG["settings"]["ignore_sheet_mark"] 
    abspath_no_ext = os.path.splitext(abspath)[0]

    if not abspath.startswith(abssource):
        logger.error(f"{abspath} 不是配置表目录下的配置")
        return

    sheets:Sequence[xw.Sheet] = workbook.sheets


    #过滤出不带*的表名
    sheets = filter(lambda sheet:not sheet.name.startswith(ignore_sheet_mark), sheets)

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
        row_values = sheet.range('A1').expand().raw_value
        data["define"] = {
            "types": row_values[0],
            "desc": row_values[1],
            "name": row_values[2]
        }
        data["table"] = list(row_values[3:])

        relative_path = os.path.join(abspath_no_ext.replace(abssource, ""), rename or org_name)
        output = absoutput+relative_path


        output_dirname = os.path.dirname(output)
        if not os.path.exists(output_dirname):
            os.makedirs(output_dirname)

        logger.info(f"导出: {abspath} => {output}")
        if custom_generator:
            exec(code, globals(), {"data":data, "output":output})
        else:
            gen_godot(data, output)

    workbook.close()


def gen_godot(data,output):
    import pprint
    import textwrap

    # 表格数据脚本模板
    template = """
    extends Reference

    static func data():
        var None = null

        data = \\
        {data}
        return data
    """
    template = textwrap.dedent(template)

    # 在这里面写你的加工逻辑
    field_names = data["define"]["name"]
    table = {}
    for row in data["table"]:
        row_data = {}
        for index,value in enumerate(row):
            field_name = field_names[index]
            row_data[field_name] = value
        table[row_data['id']] = row_data # 我们规定第一个字段是ID字段
    
    code = template.format(data=pprint.pformat(table,indent=2))

    code = textwrap.dedent(code)
    
    with open(output+".gd", 'w+') as f:
        f.write(code)

def completed_gd():
    from glob import glob
    import os
    import textwrap
    output_path = CFG['settings']['output']
    settings_file_path = os.path.join(output_path,'Settings.gd')
    project_root = CFG["settings"]["project_root"]

    lines = []

    for path in glob(f'{output_path}/**/*.*', recursive=True):
        if path == settings_file_path:
            logger.info("跳过 Settings.gd")
            continue
        basename = os.path.basename(path)
        setting_name = os.path.splitext(basename)[0]
        relpath = os.path.relpath(path, project_root).replace("\\","/")
        lines.append(f"const var {setting_name} = preload('res://{relpath}')")

    # 去掉缩进
    code = textwrap.dedent("""
    class_name Settings
    extends Object

    {refs_code}
    """)
    refs_code = '\n'.join(lines) 

    code = code.format(refs_code=refs_code)

    with open(settings_file_path, 'w') as f:
        f.write(code)




def gen_all():
    abssource = os.path.abspath(CFG["settings"]["input"])
    app = xw.App(visible=False)
    exts = [".xlsx", ".xls"]
    for ext in exts:
        full_paths = glob.glob(f"{abssource}/**/*{ext}",recursive=True)
        for full_path in full_paths:
            filename = os.path.basename(full_path)
            if filename.startswith("~$"):
                logger.warning(f"{filename} 不是配置表，跳过！")
                continue
            book = app.books.open(full_path)
            excel2dict(book)
    on_completed()
    app.quit()


def gen_one(path):
    app = xw.App(visible=False)
    book = app.books.open(path)
    excel2dict(book)
    on_completed()
    app.quit()

load_toml_config()