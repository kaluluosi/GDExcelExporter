# GDExcelExporter

这个excel表导出工具是为godot项目而开发，当然设计的比较灵活可以定制导出过程用于加工生成任何你想要的数据格式文件（你得自己写python代码去定制）

## 环境要求

pyhton版本：`>=python 3.8.1`

操作系统： windows （依赖的xlwings包只支持windows）

## 使用方法

pip上安装

```
pip install gd-excelexporter
```

或者直接git clone 这个项目、下载这个项目，在项目目录下执行

```
pip install .
```

在控制台里输入`ee`命令即可看到命令

```shell
sage: ee [OPTIONS] COMMAND [ARGS]...

  ==========Excel表导出工具 ============

Options:
  --help  Show this message and exit.

Commands:
  create-completed-hook  创建导表完成钩子脚本
  create-generator       创建生成器脚本
  gen-all                导出所有表
  gen-one                打开并导出整张excel表
  init                   生成默认配置表项目
```


## 快速开始
Godot项目使用很简单

直接到你的游戏项目里创建一个`Settings`目录，然后进入该目录执行以下命令。
![](assets/2022-01-16-02-17-03.png)

```shell
ee init
```

然后就会生成下面文件
![](assets/2022-01-16-02-25-13.png)

把你的Excel表放到data目录。
注意！Excel表有格式要求，该目录下默认有个template.xlsx是范本，你可以直接复制这个范本。

然后在这个目录下调用：

```shell
ee gen-all
```

dist目录下就会生成以下文件
![](assets/2022-01-16-02-27-01.png)
![](assets/2022-01-16-02-27-13.png)

```python
extends Reference

static func data():
    var None = null

    data = \
    { 1.0: { 'desc': None,
         'id': 1.0,
         'name': '金币',
         'overlap': -1.0,
         'sell_price': None,
         'type': '虚拟道具',
         'use_effect': False},
  10001.0: { 'desc': '飞蝗石，可以扔向敌人',
             'id': 10001.0,
             'name': '石头',
             'overlap': 100.0,
             'sell_price': 1.0,
             'type': '消耗品',
             'use_effect': 2.0}}
    return data
```

```python
extends Node

var Item = load(f'res://Settings/dist/道具/Item.gd')

```

然后把settings.gd挂到Autoload里面去。


这样你就可以快乐的在GDScript代码里这样读表了：
```python
func _ready():
    var item_data = Settings.Item.data()
    var item = item_data[10001]
    var item = item.name # => 石头
```



## exporter.toml讲解
```toml
[settings]
ignore_sheet_mark = "*"  # 如果sheet以这个符号开头，那么就跳过不导出
custom_generator = "" # 自定义生成脚本（用python写）
completed_hook = "" # 自定义导出结束钩子脚本 （用python写）
input = "data" # 你Excel表所在目录的相对路径
output = "dist" # 你要输出保存的相对路径
project_root = ".." # 项目文件夹相对于当前Settings目录的路径
```

**ignore_sheet_mark**

如果sheet以这个符号开头，那么就跳过不导出

**custom_generator**

自定义生成脚本路径（用python写），是用来覆盖默认生成逻辑的。
GDExcelExporter默认生成的是GDScript数据文件，如果你有自己的数据文件方案，比如生成json、Resource、乃至C#，又或者其他，你得自己实现。本项目Sample文件夹下有示例。

**completed_hook** 

自定义导出结束钩子脚本路径（用python写），用来覆盖导完表后的处理。
GDExcelExporter默认会在这里处理生成一个settings.gd文件，用来快速读表。
你有自己的需要可以自己实现一个脚本然后路径设置上去覆盖。

**input** 

你Excel表所在目录的相对路径

**output** 

你要输出保存的相对路径

**project_root**

这个比较难理解，简单的说就是你的`Godot游戏项目`对于`Settings目录`的相对路径。
比如你的`Settings目录`是在`Godot游戏项目目录`下，那么相对路径就是"../"，`Settings目录`的上一级就是`Godot游戏项目目录`。这样`settings.gd`生成代码里load数据文件的资源url才能正确生成，不然你可能得到的是 “res://dist/道具/Item.gd”，这就不正确了。

举个例子，你可能想要这样的效果：`Settings目录`跟`Godot游戏项目`平级，然后把数据文件导出到`Godot游戏项目`。你的目录结构是这样的：

```
--+
  |--- Godot游戏项目
  |           |
  |           +----Data
  |----Settings
```
你想从`Settings目录`把数据文件导入到`Godot游戏项目/Data`目录里

那么你的export.toml要这样配置

```toml
[settings]
ignore_sheet_mark = "*"  
custom_generator = "" 
completed_hook = "" 
input = "data" # 
output = "../Godot游戏项目/Data" 
project_root = "../Godot游戏项目" # 项目文件夹相对于当前Settings目录的路径
```

这样子 GDExcelExporter 就能够知道 `../Godot游戏项目` 才是项目根目录，从而生成“res://”路径的时候才能正确截取相对于项目目录的路径塞进去。

## Excel表格式

**sheet格式**

**注意！Excel表格式有固定要求！**
![](assets/2022-01-15-23-36-51.png)

|int|float|string|
|---|---|---|
|编号|名称|售价|
|id|name|price|
|数值|数值|数值|

上面是示例

GDExcelExporter会固定读取头三行数据，第四行开始才算是表具体数据，头三行只是定义描述，GDExcelExporter本身不会去根据这些类型作什么处理，会被存到data字典传递给custom_generator脚本供具体使用。

1. 第一行是用来定义字段类型
2. 第二行是字段中文描述
3. 第三行是字段英文名（用于生成字典的key）

除了头三行必须要有数据外，什么颜色，格式之类的没有要求，你可以随意标注颜色加批注不影响。

**Sheet名字规则**

![](assets/2022-01-15-23-37-11.png)

中文名[-生成文件名]

生成文件名是可选的，如果你希望生成的数据文件是别的名字（主要是生成英文文件名），那么你加上，不然Exporter默认传递给custom_generator的output是用中文名。


字段类型请看(字段类型支持)https://github.com/kaluluosi/GDExcelExporter/pull/3]


