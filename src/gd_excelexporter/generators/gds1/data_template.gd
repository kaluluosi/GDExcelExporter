# warnings-disable
extends Reference

var True = true
var False = false
var None = null


var data = \
{
{% for id,row in table.items()-%}
    {{id}}:{% raw %}{{% endraw %}{% for field,variant in row.items() %} "{{field}}":{{variant|cvt|safe}}, {% endfor %}{% raw %}}{% endraw %},
{% endfor %}
}

{% for id,row in table.items()-%}
    {% for field,variant in row.items() -%} 
{% if variant.type_define.type_name == "function" %}
func {{variant.field_name}}_{{id}}{{variant.type_define.params}}:
{% if variant.value -%}
{{variant.value|indent}}
{%- else -%}
    pass
{%- endif %}
{% endif %}
    {%- endfor %}
{%- endfor %}