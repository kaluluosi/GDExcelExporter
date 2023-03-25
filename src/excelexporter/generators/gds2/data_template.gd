# warnings-disable
extends RefCounted

var True = true
var False = false
var None = null


var data = \
{
{% for id,row in sheetdata.items()-%}
    {{id}}:{% raw %}{{% endraw %}{% for field,value in row.items() %} "{{field}}":{{value|cvt|safe}}, {% endfor %}{% raw %}}{% endraw %},
{% endfor %}
}

{% for id,row in sheetdata.items()-%}
    {% for field,value in row.items() -%} 
{% if value.type_define.type_name == "function" %}
func {{value.field_name}}_{{id}}{{value.type_define.params}}:
    {% if value.value -%}
    {{value.value}}
    {%- else -%}
    pass
    {%- endif %}
{% endif %}
    {%- endfor %}
{%- endfor %}