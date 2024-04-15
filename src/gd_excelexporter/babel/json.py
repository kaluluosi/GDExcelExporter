from collections import deque
from babel.messages.jslexer import tokenize, unquote_string


JSON_GETTEXT_KEYWORD = 'type'
JSON_GETTEXT_VALUE = 'gettext_string'
JSON_GETTEXT_KEY_CONTENT = 'content'
JSON_GETTEXT_KEY_ALT_CONTENT = 'alt_content'
JSON_GETTEXT_KEY_FUNCNAME = 'funcname'


class JsonExtractor(object):
    def __init__(self, data):
        self.state = 'start'
        self.data = data

        self.token_to_add = None
        self.is_value = False
        self.gettext_mode = False
        self.current_key = None
        self.results = []
        self.token_params = {}

    def add_result(self, token):
        value = unquote_string(token.value)
        if value not in self.results:
            self.results[value] = deque()
        self.results[value].append(token.lineno)

    def start_object(self):
        self.gettext_mode = False
        self.state = 'key'

    def with_separator(self, token):
        self.state = 'value'

    def end_pair(self, add_gettext_object=False):
        if self.token_to_add:
            if not self.gettext_mode or (self.gettext_mode and add_gettext_object):
                self.add_result(self.token_to_add)

        self.current_key = None
        self.state = 'key'

    def end_object(self):
        self.end_pair(add_gettext_object=True)
        self.gettext_mode = False
        self.state = 'end'

    def add_result(self, token):
        value = unquote_string(token.value)
        result = dict(
            line_number=token.lineno,
            content=value
        )
        for key, value in self.token_params.items():
            if key == 'alt_token':
                result['alt_content'] = unquote_string(value.value)
                result['alt_line_number'] = value.lineno
            else:
                result[key] = unquote_string(value)

        self.results.append(result)
        self.token_to_add = None
        self.token_params = {}

    def get_lines_data(self):
        """
        Returns string:line_numbers list
        Since all strings are unique it is OK to get line numbers this way.
        Since same string can occur several times inside single .json file the values should be popped(FIFO) from the list
        :rtype: list
        """

        encoding = 'utf-8'

        for token in tokenize(self.data.decode(encoding)):
            if token.type == 'operator':
                if token.value == '{':
                    self.start_object()
                elif token.value == ':':
                    self.with_separator(token)
                elif token.value == '}':
                    self.end_object()
                elif token.value == ',':
                    self.end_pair()

            elif token.type == 'string':
                if self.state == 'key':
                    self.current_key = unquote_string(token.value)
                    if self.current_key == JSON_GETTEXT_KEYWORD:
                        self.gettext_mode = True

                # ==value not actually used, but if only key was met (like in list) it still will be used. The important part, that key wont be parsed as value, not reversal
                if self.gettext_mode:
                    if self.current_key == JSON_GETTEXT_KEY_CONTENT:
                        self.token_to_add = token
                    elif self.current_key == JSON_GETTEXT_KEY_ALT_CONTENT:
                        self.token_params['alt_token'] = token
                    elif self.current_key == JSON_GETTEXT_KEY_FUNCNAME:
                        self.token_params['funcname'] = token.value
                else:
                    self.token_to_add = token

        return self.results


def extract_godot_json(fileobj, keywords, comment_tags, options):
    """
    Supports: gettext, ngettext. See package README or github ( https://github.com/tigrawap/pybabel-json ) for more usage info.
    """
    data = fileobj.read()
    json_extractor = JsonExtractor(data)
    strings_data = json_extractor.get_lines_data()

    for item in strings_data:
        messages = [item['content']]
        if item.get('funcname') == 'ngettext':
            messages.append(item['alt_content'])
        yield item['line_number'], item.get('funcname', 'gettext'), tuple(messages), []
