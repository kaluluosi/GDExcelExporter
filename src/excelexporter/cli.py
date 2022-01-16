import click
import textwrap
import os
from . import exporter


@click.group()
def main():
    """
    ===============================
    Excel表导出工具
    ===============================
    """
    pass


@main.command()
@click.argument("filename", nargs=1, type=click.Path(dir_okay=True), default='custom_generator')
def create_generator(filename="custom_generator.py"):
    """
    创建生成器脚本
    """
    code = """
    # 传入到此脚本的变量
    # data : 读取sheet表加工成的字典
    # {
    #   "define":{
    #       "types": ['int'...],  -- 读取的表中第一行类型定义
    #           "desc": ['描述'...], -- 读取的第二行字段描述
    #           "name": ['id'...] --读取的第三行字段名
    #   },
    #   "table":[...] -- 每一行数据的值
    # }
    # data只是把表转成字典，你要怎么加工这个字典生成你想要数据格式并生成文件需要
    # 你自己在这个脚本里实现
    # 
    # output: 导出文件。 
    # 这个路径只有文件名，没有扩展名，例子： D://dist/道具/item
    # 如果你需要有扩展名，自己加 output+=".gd"，然后自己写入文件。

    # CFG 就是export.toml配置字典，你在哪个目录下执行ee命令，那么CFG就读哪个目录的export.toml
    # CFG["settings"]["input"] -- 读取配置表目录路径
    
    # 内置jinja包，你可以：
    # import jinja 
    # 然后使用jinja模板来生成你的文件

    # 下面是示例，直接导出保存成json文件，你可以删掉下面代码用jinja模板工具
    # 用模板生成你的代码文件，然后写入output路径保存成代码文件

    def gen(data, output):
        # 在这里面写你的加工逻辑
        import json
        with open(output+".json",'w+', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    gen(data,output)
    """
    with open(filename+".py", 'w+', encoding='utf-8') as f:
        f.write(textwrap.dedent(code))


@main.command()
def create_completed_hook():
    """
    创建导表完成钩子脚本
    """
    code = """
    # 钩子脚本组要是用于在导表结束后处理别的事务用
    # gen-all命令会在所有表导完后调用
    # gen-one命令会在导完这个表后调用

    # 最典型的用法是用来搜集所有配置表生成读表util:

    # class_name Settiings
    # Settings.gd
    # const var Item = preload("res://Data/Item/Item.gd")
    # ...

    # 以后在代码里想要读这个表你可以
    # Settings.Item.data()

    # todo:具体要怎么实现看自己需求

    """
    code = textwrap.dedent(code)
    with open("completed_hook.py", 'w+') as f:
        f.write(code)


@main.command()
def init():
    """
    生成默认配置表项目
    """
    exporter.create_toml_config()
    os.mkdir(exporter.CFG["settings"]["input"])
    os.mkdir(exporter.CFG["settings"]["output"])
    

@main.command()
@click.option("--cwd", default=".", help="工作目录，执行命令所在的目录")
def gen_all(cwd):
    """
    导出所有表
    """
    exporter.gen_all(cwd)
        
@main.command()
@click.option("--cwd", default=".", help="工作目录，执行命令所在的目录")
@click.argument("file", type=click.Path(True))
def gen_one(file:str,cwd):
    """
    打开并导出整张excel表
    """
    exporter.gen_one(file,cwd)

