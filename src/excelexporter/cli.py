import shutil
import click
import textwrap
import logging
import os
import pkg_resources
from excelexporter.config import Configuration

logger = logging.getLogger(__name__)


@click.group
def main():
    """
    ===============================
    Excel表导出工具
    ===============================
    """
    pass


@main.command
@click.option(
    "--setting-dir", "-d",
    is_flag=True,
    default=True,
    prompt="创建并放在Setting目录？"
)
def init(setting_dir: bool):
    """
    生成默认配置表项目
    """
    setting_dir_name = "Setting"

    if setting_dir:
        if os.path.exists(setting_dir_name) and os.listdir(setting_dir_name):
            click.echo(f"{setting_dir_name} 已经存在并且非空!")
            return

        os.mkdir(setting_dir_name)
        os.chdir(setting_dir_name)

    config = Configuration()
    input_dir = click.prompt(
        "输入存放excel表格目录名称", default=config.input, show_default=True)
    output_dir = click.prompt(
        "输入存放导出文件目录名称", default=config.output, show_default=True)

    template_xlsx_path = pkg_resources.resource_filename(
        __package__,
        "template/示例.xlsx"
    )

    if os.path.exists(input_dir) and os.listdir(input_dir):
        click.echo(f"{input_dir}已经存在并且非空!")
        return
    if os.path.exists(output_dir) and os.listdir(output_dir):
        click.echo(f"{output_dir}已经存在并且非空!")
        return

    os.mkdir(input_dir)
    os.mkdir(output_dir)
    config.input = input_dir
    config.output = output_dir
    config.save()

    shutil.copy(template_xlsx_path, input_dir)
    click.echo("配置表项目生成完毕，后续你可以通过修改export.toml调整配置。")


@main.command()
@click.option("--cwd", default=".", help="工作目录，执行命令所在的目录")
def gen_all(cwd):
    """
    导出所有表
    """
    # exporter.gen_all(cwd)
    pass


@main.command()
@click.option("--cwd", default=".", help="工作目录，执行命令所在的目录")
@click.argument("file", type=click.Path(True))
def gen_one(file: str, cwd):
    """
    打开并导出整张excel表
    """
    # exporter.gen_one(file, cwd)
    pass


if __name__ == "__main__":
    main()
