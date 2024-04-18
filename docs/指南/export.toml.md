# export.toml配置文件

`export.toml`配置文件定义了Settings目录的导出参数。

```toml
version = "1.0.0"
engine = "xlrd"
ignore_sheet_mark = "~" 
ignore_field_mark = "*"
custom_generator = "GDS2.0"
input = "data"
output = "dist"
project_root = "../"

[localization]
babel_keywords = [
    "tr",
    "Label/text",
    "Label/tooltip_text",
    "Button/text",
    "Button/tooltip_text",
    "TextEdit/text",
    "TextEdit/tooltip_text",
    "TextEdit/placeholder_text",
    "TextEdit/tooltip_text",
    "LineEdit/text",
    "LineEdit/tooltip_text",
    "LineEdit/placeholder_text",
    "RichTextLabel/textRichTextLabel/tooltip_text",
]
pot_file = "lang/template.pot"


```

* version： 指定gd-excelexporter版本。
* engine： 指定数据源解析器，默认为xlrd。
* ignore_sheet_mark： 忽略的sheet名称前缀，默认为~，如果sheet名称以~开头，则不会被导出。
* ignore_field_mark： 忽略的字段名称前缀，默认为*，如果字段名称以*开头，则不会被导出。
* custom_generator： 指定自定义导出器，默认为GDS2.0，如果指定了自定义导出器，则使用。
* input： 指定数据源目录，默认为data目录。
* output： 指定导出目录，默认为dist目录。
* project_root： 指定项目根目录，默认为../。一般来讲我们的Settings目录会放置在游戏项目根目录下，而Settings目录的上级目录`../`就是项目根目录。这个参数用来辅助计算导出文件的相对路径。

**localization** （POT本地化功能配置）

* babel_keywords： 指定需要进行翻译抽取的字段，目前涵盖了大部分文本控件的静态文本字段。你如果看明白怎么添加你可以自己修改添加。
* pot_file： 指定导出的pot文件路径。

!!! warning 
    一般情况下，我们不需要修改`export.toml`配置文件，除非你的项目结构与默认的有所不同。比如你的Settings目录不在项目根目录下，是独立放在别的目录，然后你又想要把数据导出到项目目录，那么你就需要修改`input` `output` `project`。

    