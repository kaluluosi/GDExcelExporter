# excel表规范

## Sheet子表

excel文档可以视为一个目录，而它的sheet则是具体的每一个数据文件。
`ee`导出excel文档的时候会在`output`目录创建一个同名目录，然后将每个sheet导出成目标数据文件按sheet名保存。

例子：

示例.xlsx，有名为demo的sheet，导出后如下。
![](../images/2023-08-14-11-48-39.png)
![](../images/2023-08-14-11-49-30.png)

`ee`创建了示例目录，然后将名为demo的sheet导出成demo.gd。

## sheet导出的dict格式

假如我们的sheet如下：

| id   | name | age | sex |
| ---- | ---- | --- | --- |
| 1000 | 张三 | 18  | 男  |

导出后，`ee`会生成一个名为`demo.gd`的文件，内容如下：


```json
{
    "1000": {
    "id":1000,
    "name": "张三",
    "age": 18,
    "sex": "男"}
}

```
!!! warning
    所有的sheet的`A`列（第一列）都会作为id列，作为导出的`dict`的`key`。


## 字段类型介绍

`ee` 支持字段类型有以下

![](../images//2023-08-14-11-51-54.png)

### id


id类型，`int`类型的别名。是用来做唯一标识的，例如：
| id |
| 编号 |
| ---- |
| 1    |

会被导出成:
```go

{
    '1':{'id':1}
}

```

!!! note
    你并不是非得用`id`类型来作为编号列，你也可以用`str`类型。
    只要那个类型可以作为字典的`key`(可hash类型)就可以。不过`ee`推荐用`id`类型作为编号列，因为这是业内常用的做法。
    但是如果你的表是一张枚举、常量表，那么用`str`类型作为编号列是合理的。

| string | int   |
| ------ | ----- |
| key    | value |
| MAX_HP | 1000  |
| MAX_MP | 1000  |

```json
{
    'MAX_HP':{'key':'MAX_HP', value':1000},
    'MAX_MP':{'key':'MAX_MP','value':1000}
}
```

### int

整数类型字段，例如：
| id  | int |
| --- | --- |
| id  | age |
| 1   | 20  |

会被导出成:
```go

{
    '1':{'id':1,'age':20}
}

```

!!! note
    `int`类型的特点是会将任何填入的数字转换成整数（取整）

### float

浮点数类型字段，例如：

| id  | float   |
| --- | ------- |
| id  | timeout |
| 1   | 20.0    |

会被导出成:
```go
{
    '1':{'id':1,'timeout':20.0}
}

```



### string

字符串类型，例如：

|id| string |
|_| ------ |
|id|| name   |
|10| 张三   |

会被导出成:
```go

{
    id:10,
    name:"张三"
}

```

### bool

布尔类型字段，例如：

| id  | bool  |
| --- | ----- |
| id  | is_ok |
| 1   | TRUE  |

会被导出成:
```go
{
    '1':{'id':1,'is_ok':true}
}

```

!!! note
    bool类型字段能够识别excel中的`TRUE` `FALSE` 转换成布尔类型。


### array

数组类型字段，用`|`分隔，例如：

| id  | array      |
| --- | ---------- |
| id  | list       |
| 1   | 20\|'2'\|3 |
会被导出成:
```go

{
    '1':{'id':1,'list':[20,'2',3]}
}

```

!!! warning
    array类型数组是原始数组，支持任何数据类型但是你必须显式的按gds语法写字面量。
    比如： 字符串你必须加双引号 '2' 。
    因为array的导出是粗暴的将字符串 split("|")，然后就直接生成到代码，并没有做任何的转换，他也无法做任何的转换，因为他不知道每个元素具体应该是什么类型。

### array_str
数组字符串，用`|`分隔，例如：

| id  | array_str           |
| --- | ------------------- |
| id  | array_str           |
| 1   | a         \| b \| c |

会被导出成:
```go
{
    '1':{'id':1,'array_str':['a','b','c']
}

```

!!! note: 
    `array_str`是为了方便配置字符串数组而特别定义的，他跟`array`的区别是，`array_str`配置的字符串可以省略`'` `"`。当然你也可以手动加上引号 \`a\`|\`b\`|\`c\`。`ee` 会自动识别转换。同时这个字段即便配置了数字元素也会被转换成字符串。

### array_bool

数组布尔类型，用`|`分隔，例如：
| id  | array_bool    |
| --- | ------------- |
| id  | array_bool    |
| 1   | TRUE\|FALSE\| |

会被导出成:
```go
{
    '1':{'id':1,'array_bool':[true,false]}
}
```

!!! note
    `array_bool`是为了方便配置布尔值数组特别定义的，他会将`TRUE`和`FALSE`转换成布尔值。


### dict

字典类型，用`|`分隔，例如：
| id  | dict                   |
| --- | ---------------------- |
| id  | dict                   |
| 1   | "name":"Tom"\|"age":10 |

会被导出成:
```go
{
    '1':{'id':1,'dict':{'name':'Tom','age':10}}
}
```

!!! warning
    字典类型必须使用python字面量语法定义。因为`ee`是直接将字典定转写到数据文件，并没有做任何的转换，所以必须使用python语法。

### function

函数类型，例如：

| id  | function    |
| --- | ----------- |
| id  | function    |
| 1   | print(args) |

会被导出成:
```go
{
    '1':{'id':1,'function':Callable(self,'function_1')}
}

static def function_1(args=[]):
    print(args)
```

!!! note
    function类型的参数是`args=[]`，是个泛用参数列表。这个函数要如何传参，还有位置参数到底如何使用和处理，完全看程序员自己私下的约定。
    可用显式参数列表版本的function类型，来解决这个参数列表的问题。

显式参数函数类型，例如：

| id  | function(a,b=null,c=null) |
| --- | ------------------------- |
| id  | function                  |
| 1   | print(args)               |

会被导出成:
```go
{
    '1':{'id':1,'function':Callable(self,'function_1')}
}

static def function_1(a,b=null,c=null):
    print(a)
    print(b)
    print(c)
```

!!! note
    显式参数函数类型，参数列表是显式定义的，Godot编辑器语法检查的时候可以会约束参数列表。相对于泛用参数列表，显式参数可以更容易约束和看出函数参数。

------------------------------

!!! info
    下面是本地化字段类型，这些字段类型的配置值会抽取到POT文件中用于多语言翻译。
    POT是Godot支持的多语言翻译文件格式/方案--[使用gettext进行本地化](https://docs.godotengine.org/zh-cn/4.x/tutorials/i18n/localization_using_gettext.html#advantages)。

!!! note
    Godot支持两种本地化多语言方案
    - 翻译表（.translation）基于csv键值对的那种传统多语言表 -- [是游戏国际化](https://docs.godotengine.org/zh-cn/4.x/tutorials/i18n/internationalizing_games.html#)
    - POT文件（.pot）基于gettext的POT文件。 --[使用gettext进行本地化](https://docs.godotengine.org/zh-cn/4.x/tutorials/i18n/localization_using_gettext.html#advantages)

    前者是先在多语言表录入`key`和`文本`，然后代码中用`tr()`读取。也就是说是需要先录入，再使用。
    后者是相反的，是先在代码中使用，通过`babel`之类的工具抽取到POT语言表中。

    POT比传统多语言表有以下优势：
    1. 研发期间不需要先添加翻译key，直接代码中正常开发即可，用`tr()`将需要翻译的字符串包起来。
    2. Godot会自动抽取场景、tres等文件中文本字段到POT。
    3. 自动除重，相同的字符串会合并成一条翻译。
    4. 差异更新，不用像语言表那样手动管理增删。
    5. 翻译工具更先进完备，`Poedit`编辑器或者Transifex 和 Weblate 等翻译平台来进行本地化翻译，然后导出成`.po`文件。


### tr_string

本地化字符串，例如：

| id  | tr_string    |
| --- | ------------- |
| id  | tr_string    |
| 1   | name|

会被导出成:
```go
{
    '1':{'id':1,'tr_string':"name"}
}
```

!!! note
    `tr_string`和`string`的区别在于`tr_string`会被抽取到POT文件中用于多语言翻译。


### tr_dict

本地化字典，例如：

| id  | tr_dict          |
| --- | ----------------- |
| id  | tr_dict          |
| 1   | "name":"Tom"\|"age":10 |

会被导出成:
```go
{
    '1':{'id':1,'tr_dict':{'name':'Tom','age':10}}
}
```

!!! note
    `tr_dict`和`dict`的区别在于`tr_dict`会被抽取到POT文件中用于多语言翻译。
    **只会抽取string类型value。**


### tr_array_str

本地化数组字符串，例如：

| id  | tr_array_str           |
| --- | ---------------------- |
| id  | tr_array_str           |
| 1   | "a"\|"b"\|"c" |

会被导出成:
```go
{
    '1':{'id':1,'tr_array_str':['a','b','c']}
}
```

!!! note
    `str_array_str`和`array_str`的区别在于`str_array_str`会被抽取到POT文件中用于多语言翻译。


