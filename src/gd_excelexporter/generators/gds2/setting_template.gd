# warnings-disable
extends Node
# 这个脚本你需要挂到游戏的Autoload才能全局读表

{% for line in lines -%}
{{line}}
{% endfor %}