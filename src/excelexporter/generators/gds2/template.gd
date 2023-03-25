extends Reference
var None = null
var False = false
var True = true

var data = \
{
    {% for id,row in sheetdata.items()%}
        {{id}}:{% raw %}{{% endraw %}{% for field,value in row.items() %} "{{field}}":{{value|cvt|safe}}, {% endfor %}{% raw %}}{% endraw %},
    {% endfor %}
}

