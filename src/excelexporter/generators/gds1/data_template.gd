# warnings-disable
extends Reference

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
    {{value.value}}
        {% endif %}
    {%- endfor %}
{% endfor %}