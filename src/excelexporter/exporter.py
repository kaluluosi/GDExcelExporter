import importlib
import os
import xlwings as xw
import glob


from .logger import logger
from toml import load, dump
from .generator.godot_script import (
    generator as GodotScriptGenerator,
    completed as GodotScriptCompleted
)

CFG = {
    "settings": {
        "ignore_sheet_mark": "~",  # 带星号的sheet不会导出
        "ignore_field_mark": "*",  # 字段忽略标志
        "custom_generator": "",  # 自定义加工脚本
        "completed_hook": "",  # 导表结束后调用脚本
        "input": "data",  # 导入目录
        "output": "dist",  # 导出目录
        # 导出到项目的路径，比如你的 output="../Godot项目/Scripts/Settings"，
        # 那么project_root="../Godot项目"
        "project_root": "../",
    }
}


def load_toml_config(filename: str = "export.toml"):
    """加载toml配置文件

    Raises:
        FileNotFoundError: 配置文件不存在的时候抛出

    Returns:
        dict: 配置数据字典，字段定义看CFG变量
    """

    local_cfg_path = os.path.abspath(filename)
    if os.path.exists(local_cfg_path):
        cfg_data = load(local_cfg_path)
        CFG["settings"].update(cfg_data["settings"])
    else:
        logger.warning(f"配置文件 {local_cfg_path} 不存在！将使用默认配置尝试导出。")


def create_default_toml_config():
    """
    用CFG模板创建一个默认的toml配置文件
    """
    with open("export.toml", "w+", newline="\n", encoding="utf-8") as f:
        dump(CFG, f)


def on_completed():
    """
    导表结束钩子
    """
    completed_hook = CFG["settings"]["completed_hook"]

    completed = GodotScriptCompleted

    if completed_hook:

        if os.path.isfile(completed_hook):
            logger.info(f"尝试加载用户自定义结束钩子 {completed_hook}")
            with open(completed_hook) as f:
                code = f.read()
                exec(code)
        else:
            try:
                logger.info(f"尝试加载内置结束钩子 {completed_hook}")
                module = importlib.import_module(completed_hook)
                completed = getattr(module, 'completed', completed)
            except Exception:
                logger.warning(f"{completed_hook} 不是内置结束钩子！请检查配置。")
                pass

    code = completed(CFG)
    code = "# 本文件由代码生成，不要手动修改" + code
    output_path = CFG["settings"]["output"]

    settings_file_path = os.path.join(output_path, "settings.gd")
    with open(settings_file_path, "w", newline="\n", encoding="utf-8") as f:
        f.write(code)
    logger.info("导表结束：Setting.gd 更新完毕!")


def excel2dict(workbook: xw.Book):
    """Excel表转字典对象

    Args:
        workbook (xw.Book): 工作簿
    """
    abspath: str = workbook.fullname
    abssource = os.path.abspath(CFG["settings"]["input"])
    absoutput = os.path.abspath(CFG["settings"]["output"])
    ignore_sheet_mark = CFG["settings"]["ignore_sheet_mark"]
    abspath_no_ext = os.path.splitext(abspath)[0]

    if not abspath.startswith(abssource):
        logger.error(f"{abspath} 不是配置表目录下的配置")
        return

    # 过滤出不带*的表名
    sheets = filter(
        lambda sheet: not sheet.name.startswith(ignore_sheet_mark),
        workbook.sheets
    )
    generator = GodotScriptGenerator  # 默认导出器

    custom_generator = CFG["settings"]["custom_generator"]
    if custom_generator:
        if os.path.isfile(custom_generator):
            with open(custom_generator) as f:
                custom_code = f.read()
                exec(custom_code)  # 执行后generator会被替换成字自定义generator
                logger.info(f"使用 {custom_generator} 自定义导出器")
        else:
            try:
                logger.info(f"尝试加载内置导出器 {custom_generator}")
                module = importlib.import_module(custom_generator)
                generator = getattr(module, 'completed', generator)
            except Exception:
                logger.warning(f"{custom_generator} 不是内置导出器！请检查配置。")
                pass

    for sheet in sheets:
        try:
            # 解析表名
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

            code, ext = generator(data, CFG)  # 将字典传递给导出器
            code = "# 本文件由代码生成，不要手动修改\n"+code

            output = f"{output}.{ext}"
            with open(output, 'w', encoding='utf-8', newline='\n') as f:
                f.write(code)
                logger.info(f"导出: {abspath}:{sheet.name} => {output}")
        except Exception:
            logger.error(
                f"{sheet.name} 导出失败！"
            )

    workbook.close()


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
                try:
                    excel2dict(book)
                except Exception:
                    logger.error(
                        f"{book.fullname}导出失败！"
                    )
        on_completed()


def gen_one(path, cwd: str = "."):
    with xw.App(visible=False) as app:
        book = app.books.open(path)
        try:
            excel2dict(book)
        except Exception:
            logger.error(
                f"{book.fullname}导出失败！"
            )
        on_completed()
