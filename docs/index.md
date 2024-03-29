# GDExcelExporter

GDExcelExpoter 是为Godot设计的Excel表格导出数据资源的工具。
它内置了好几种数据表导出和读取方案（导出器），支持Godot3.x、Godot4.x。

>下面我们用`ee`代指`GDExcelExporter`。

!!! warning 
    2.0 开始导出格式已经不兼容1.0，如果你的项目里已经大量使用1.0导出的数据表，可能会导致你要修改代码的地方非常多。

## 为什么需要这个工具？

Unreal引擎中有一个工具叫做DataTable，它的作用是充当一个小型的数据库给游戏设计人员编辑配置数值数据。

打个比方，我们游戏中有道具系统，而道具整个对象一旦属性字段建模好，那么就可以通过配置这些属性定义出各种各样的道具。

而这些数据在没有DataTable的时候我们要么在脚本代码里用一个字典写，要么在Json文件里写，维护十分麻烦。数据库（即便是sqlite）又太过重量级，同时数据库十分不利于编辑和测试，数据库的读取接口也十分繁琐不够直接。

因此Unreal引擎的解决办法是在引擎内部开发了个轻量级文件数据库-DataTable，我们可以把海量的数据条目填写在各种DataTable中，然后程序员可以直接的访问这些DataTable读取里面的数据。

然而，中国游戏开发人员更懂得折中。因为我们的Office Excel表格工具本质上讲就是一个轻量级文件数据库，并且作为生产力工具发展这么多年，强大的数据处理能力，支持vbs脚本扩展，非常适合充当数据管理工具。

因此就有了用Excel表格来作为DataTable的做法。

GDExcelExporter只是个搬运工，他把按照他的规格设计的表格读取转换生成游戏引擎里能够直接读取的数据文件。

!!! warning
    他不是数据库，并不是给你用来将数据写回excel保存用的。

有了这个工具：

1. 就不用手写json。
2. 也不用嵌入sqlite。
3. 由于数据是以项目的文件资源存在，因此也是版本管理工具友好的。
4. 也因为数据是文件资源，因此热更新友好。
5. 你不需要学习别的工具去编辑维护数据，会用excel就可以，你可以用上你excel中所有的技巧去编辑数据，可以批量快速生产。


## 内置导出器

导出器是指将excel表格导出目标格式的程序。目前 `ee` 内部支持以下导出器：

| 导出器ID | 导出器名称      | Godot 3.x | Godot 4.x | C#     | 支持代码配置 |
| -------- | --------------- | --------- | --------- | ------ | ------------ |
| GDS1.0   | GodotScript 1.0 | ✔         | ❌         | ❌      | 支持         |
| GDS2.0   | GodotScript 2.0 | ❌         | ✔         | ❌      | 支持         |
| RESOURCE | Resource        | ✔         | ✔         | ✔      | 不支持       |
| JSON1.0  | Json            | ✔         | ✔         | ✔      | 不支持       |
| JSON2.0  | Json            | ✔         | ✔         | ✔      | 不支持       |
| C#       | CSharp          | 未开发    | 未开发    | 未开发 | 未开发       |
