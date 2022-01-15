
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
import json


def gen(data, output):
    import textwrap
    import pprint

    # 表格数据脚本模板
    template = """
    extends Reference

    static func data():
        var None = null

        var data = \\
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

gen(data,output)
