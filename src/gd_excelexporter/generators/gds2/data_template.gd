# warnings-disable
extends RefCounted

@warning_ignore("unused_variable")
var True = true
@warning_ignore("unused_variable")
var False = false
@warning_ignore("unused_variable")
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
@warning_ignore("unused_parameter")
func {{variant.field_name}}_{{id}}{{variant.type_define.params}}:
{% if variant.value -%}
{{variant.value|indent}}
{%- else -%}
    pass
{%- endif %}
{% endif %}
    {%- endfor %}
{%- endfor %}