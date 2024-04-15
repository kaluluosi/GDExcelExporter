import re

# thanks: https://github.com/remram44/pybabel-godot/edit/master/babel_godot.py

__version__ = '1.2'


_godot_node = re.compile(r'^\[node name="([^"]+)" (?:type="([^"]+)")?')
_godot_property_str = re.compile(
    r'^([A-Za-z0-9_]+)\s*=\s*([\["].+)\Z',
    re.DOTALL,
)


class StringReader(object):
    def __init__(self, lineno):
        self.result = []
        self.lineno = lineno

    def parse_line(self, string):
        escaped = False
        for i, c in enumerate(string):
            if escaped:
                if c == '\\':
                    self.result.append('\\')
                elif c == 'n':
                    self.result.append('\n')
                elif c == 't':
                    self.result.append('\t')
                else:
                    self.result.append(c)
                escaped = False
            else:
                if c == '\\':
                    escaped = True
                elif c == '"':
                    return string[i + 1:]
                else:
                    self.result.append(c)
        return None

    def get_result(self):
        return [(''.join(self.result), self.lineno)]


class ArrayReader(object):
    def __init__(self, lineno):
        self.result = []
        self.string = None
        self.lineno = lineno

    def parse_line(self, string):
        lineno = self.lineno
        self.lineno += 1

        if self.string is not None:
            remainder = self.string.parse_line(string)
            if remainder is None:
                return None
            self.result.extend(self.string.get_result())
            string = remainder
            self.string = None

        i = 0
        while i < len(string):
            c = string[i]
            if c in ' \t,':
                i = i + 1
            elif c == ']':
                return string[i + 1:]
            elif c == '"':
                self.string = StringReader(lineno)
                remainder = self.string.parse_line(string[i + 1:])
                if remainder is None:
                    return None
                else:
                    self.result.extend(self.string.get_result())
                    string = remainder
                    self.string = None
                    i = 0
            else:
                raise ValueError("Unexpected character %r" % (c,))

        raise ValueError("Unterminated array")

    def get_result(self):
        return self.result


def extract_godot_scene(fileobj, keywords: list, comment_tags, options):
    """Extract messages from Godot scene files (.tscn).

    :param fileobj: the seekable, file-like object the messages should be
                    extracted from
    :param keywords: a list of property names that should be localized, in the
                     format '<NodeType>/<name>' or '<name>' (example:
                     'Label/text')
    :param comment_tags: a list of translator tags to search for and include
                         in the results (ignored)
    :param options: a dictionary of additional options (optional)
    :rtype: iterator
    """
    encoding = options.get('encoding', 'utf-8')

    current_node_type = None

    properties_to_translate = {}
    for keyword in keywords:
        if '/' in keyword:
            properties_to_translate[tuple(keyword.split('/', 1))] = keyword
        else:
            properties_to_translate[(None, keyword)] = keyword

    def check_translate_property(property):
        keyword = properties_to_translate.get((current_node_type, property))
        if keyword is None:
            keyword = properties_to_translate.get((None, property))
        return keyword

    current_value = keyword = None

    for lineno, line in enumerate(fileobj, start=1):
        line = line.decode(encoding)

        if current_value:
            remainder = current_value.parse_line(line)
            if remainder is None:  # Still un-terminated
                pass
            elif remainder.strip():
                raise ValueError("Trailing data after string")
            else:
                for value, value_lineno in current_value.get_result():
                    yield (
                        value_lineno,
                        keyword,
                        [value],
                        [],
                    )
                current_value = None
            continue

        match = _godot_node.match(line)
        if match:
            # Store which kind of node we're in
            current_node_type = match.group(2)
            # Instanced packed scenes don't have the type field,
            # change current_node_type to empty string
            current_node_type = current_node_type \
                if current_node_type is not None else ""
        elif line.startswith('['):
            # We're no longer in a node
            current_node_type = None
        elif current_node_type is not None:
            # Currently in a node, check properties
            match = _godot_property_str.match(line)
            if match:
                property = match.group(1)
                value = match.group(2)
                keyword = check_translate_property(property)
                if keyword:
                    if value[0:1] == '[':
                        current_value = ArrayReader(lineno)
                    else:
                        current_value = StringReader(lineno)
                    remainder = current_value.parse_line(value[1:])
                    if remainder is None:
                        pass  # Un-terminated string
                    elif not remainder.strip():
                        for value, value_lineno in current_value.get_result():
                            yield (value_lineno, keyword, [value], [])
                        current_value = None
                    else:
                        raise ValueError("Trailing data after string")


def extract_godot_resource(fileobj, keywords, comment_tags, options):
    """Extract messages from Godot resource files (.res, .tres).

    :param fileobj: the seekable, file-like object the messages should be
                    extracted from
    :param keywords: a list of property names that should be localized, in the
                     format 'Resource/<name>' or '<name>' (example:
                     'Resource/text')
    :param comment_tags: a list of translator tags to search for and include
                         in the results (ignored)
    :param options: a dictionary of additional options (optional)
    :rtype: iterator
    """
    encoding = options.get('encoding', 'utf-8')

    properties_to_translate = {}
    for keyword in keywords:
        if keyword.startswith('Resource/'):
            properties_to_translate[keyword[9:]] = keyword

    def check_translate_property(property):
        return properties_to_translate.get(property)

    current_value = keyword = None

    for lineno, line in enumerate(fileobj, start=1):
        line = line.decode(encoding)

        if current_value:
            remainder = current_value.parse_line(line)
            if remainder is None:
                pass  # Still un-terminated
            elif remainder.strip():
                raise ValueError("Trailing data after string")
            else:
                for value, value_lineno in current_value.get_result():
                    yield (
                        value_lineno,
                        keyword,
                        [value],
                        [],
                    )
                current_value = None
            continue

        if line.startswith('['):
            continue

        match = _godot_property_str.match(line)
        if match:
            property = match.group(1)
            value = match.group(2)
            keyword = check_translate_property(property)
            if keyword:
                if value[0:1] == '[':
                    current_value = ArrayReader(lineno)
                else:
                    current_value = StringReader(lineno)
                remainder = current_value.parse_line(value[1:])
                if remainder is None:
                    pass  # Un-terminated string
                elif not remainder.strip():
                    for value, value_lineno in current_value.get_result():
                        yield (value_lineno, keyword, [value], [])
                    current_value = None
                else:
                    raise ValueError("Trailing data after string")
