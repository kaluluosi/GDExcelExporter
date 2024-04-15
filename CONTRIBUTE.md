# 参与贡献

想要参与这个项目的维护和修改要怎么做？

## 先Fork
你先Fork这个项目到自己仓库里，再按下面教程设置好开发环境。
开发完毕自己测试过后创建个`pull request`给我。

## 开发环境

1. python版本要求 `>=3.8.1`
2. IDE建议用`vscode`
3. 本项目用`poetry`做包管理
4. 项目路径不可以有中文字符（poetry不支持）

## 项目环境初始化

先安装`poetry`

```shell
pip install poetry
```

然后在项目根目录下用命令行执行

```shell
poetry install
```

这个命令会自动帮我们创建虚拟环境、安装依赖，然后打印虚拟环境路径给我们。

接着在vscode状态栏的`python解析器`列表里选择刚才日志打印的虚拟环境。

然后新建一个终端或者关闭重开vscode。

当你看到下面这样命令行前有个括号写着虚拟环境名就可以了。

```shell
(gd-gd_excelexporter-py3.11) PS H:\projects\GDExcelExporter\test>
```

`poetry`相关教程请去他们官网看文档。



