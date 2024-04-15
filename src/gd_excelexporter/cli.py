import shutil
import click
import logging
import os
import pkg_resources
import gd_excelexporter

from gd_excelexporter import utils
from gd_excelexporter.engines import XlwingsEngine

# from babel import *  # noqa
from babel.messages.frontend import CommandLineInterface
from gd_excelexporter.config import Configuration


logger = logging.getLogger(__name__)


@click.group
def cli():
    """
    ===============================

    Godot Excel表导出工具

    ===============================
    """
    pass


@cli.command
def init():
    """
    生成默认配置表项目
    """
    config = Configuration()

    # 询问数据表存放目录
    datatable_dir = click.prompt(
        "输出数据表目录名", default="settings", show_default=True
    )
    if os.path.exists(datatable_dir) and os.listdir(datatable_dir):
        click.echo(f"{datatable_dir} 已经存在并且非空!")
        return

    os.mkdir(datatable_dir)
    cwd_backup = os.getcwd()
    os.chdir(datatable_dir)

    input_dir = click.prompt(
        "输入存放excel表格目录名称", default=config.input, show_default=True
    )
    output_dir = click.prompt(
        "输入存放导出文件目录名称", default=config.output, show_default=True
    )

    template = pkg_resources.resource_filename(__package__, "template")  # type: ignore

    generator = click.prompt(
        "使用哪个内置导出器？",
        type=click.Choice(list(utils.discover_generator().names)),
        default="GDS2.0",
    )

    config.input = input_dir
    config.output = output_dir

    os.mkdir(input_dir)
    os.mkdir(output_dir)
    os.mkdir("lang")  # 创建多语言目录
    config.custom_generator = generator
    config.save()

    shutil.copytree(template, os.curdir, dirs_exist_ok=True)

    os.chdir(cwd_backup)
    click.echo("配置表项目生成完毕，后续你可以通过修改export.toml调整配置。")


@cli.command()
def version():
    """
    打印ee版本号
    """
    print(gd_excelexporter.__version__)  # noqa


@cli.command(name="list")
def _list():
    """
    列出支持的导出器插件
    """
    generators = utils.discover_generator()
    if generators.names:
        for gen in generators.names:
            print(gen)


@cli.command
def add_context_menu():
    """
    添加上下文菜单（通过注册表）
    """

    dir = pkg_resources.resource_filename(__package__, "template/reg")  # type: ignore
    os.system(f"start {dir}")


def _find_config():
    if not os.path.exists("export.toml"):
        logger.error("当前目录下没有export.toml配置文件")
        logger.error("尝试往上层找")
        upper_path = os.path.join(os.curdir, os.pardir, "export.toml")
        if not os.path.exists(upper_path):
            logger.error("完全不存在export.toml,终止导表")
            raise FileNotFoundError("完全不存在export.toml,终止导表")
        else:
            os.chdir(os.pardir)


@cli.command
@click.option("--cwd", default=".", help="工作目录，执行命令所在的目录")
def gen_all(cwd):
    """
    导出所有表
    """
    os.chdir(cwd)
    _find_config()

    config = Configuration.load()

    with XlwingsEngine(config) as engine:
        engine.gen_all()


@cli.command
@click.argument("file", type=click.Path(True))
def gen_one(file: str):
    """
    打开并导出整张excel表
    """
    abs_filepath = os.path.abspath(file)
    _find_config()

    config = Configuration.load()
    with XlwingsEngine(config) as engine:
        engine.gen_one(abs_filepath)


@cli.command
@click.option("--cwd", default=".", help="工作目录，执行命令所在的目录")
def extract(cwd):
    """
    导出多语言表 gd,供 babel生成语言表用
    """
    os.chdir(cwd)
    _find_config()
    config = Configuration.load()
    with XlwingsEngine(config) as engine:
        with engine.extract_lang():
            babel_keywords = config.localization.babel_keywords
            pot_file = config.localization.pot_file

            keyword_args = [f"-k {kw} " for kw in babel_keywords]

            cfg_file = os.path.abspath("babel.cfg")

            CommandLineInterface().run(  # noqa
                [
                    "pybabel",
                    "extract",
                    "-F",
                    cfg_file,
                    *keyword_args,
                    "-o",
                    pot_file,
                    config.project_root,
                ]
            )


if __name__ == "__main__":
    cli()
