from babel.messages.jslexer import tokenize, unquote_string


# This helper is copied to all necessary files because
# once again python imports are being a pain
def reopen_normal_read(file_obj, encoding):
    """Re-open a file obj in plain read mode"""
    return open(file_obj.name, "r", encoding=encoding)


class ActiveCall:
    def __init__(self, name, parenthesis_level):
        self.name = name
        self.current_value = None
        self.value_start_line = 0
        self.stored_parenthesis_level = parenthesis_level

    def valid(self):
        return self.name and self.current_value


class CSharpExtractor(object):
    def __init__(self, data):
        self.data = data

        self.current_name = None
        self.active_calls = []

        self.parenthesis_level = 0

        self.results = []

    def start_call(self):
        self.active_calls.append(ActiveCall(
            self.current_name, self.parenthesis_level))
        self.parenthesis_level = 0
        self.current_name = None

    def end_call(self):
        call = self.active_calls.pop()

        self.parenthesis_level = call.stored_parenthesis_level

        if call.valid():
            self.add_result(call)

    def add_result(self, call):
        result = dict(
            line_number=call.value_start_line,
            content=call.current_value,
            function_name=call.name
        )
        self.results.append(result)

    def get_lines_data(self):
        """
        Returns string:line_numbers list
        Since all strings are unique it is OK to get line numbers this way.
        :rtype: list
        """
        trigger_call_prime = False

        for token in tokenize(self.data, jsx=False):
            call_primed = trigger_call_prime
            trigger_call_prime = False

            if token.type == 'operator':
                if token.value == '(':
                    if call_primed:
                        self.start_call()
                    else:
                        self.parenthesis_level += 1
                elif token.value == ')':
                    if self.parenthesis_level == 0:
                        self.end_call()
                    else:
                        self.parenthesis_level -= 1
            elif token.type == 'name':
                trigger_call_prime = True
                self.current_name = token.value
            elif token.type == 'string' and len(self.active_calls) > 0:
                string_value = unquote_string(token.value)

                call = self.active_calls[-1]

                if call.current_value is None:
                    call.current_value = string_value
                    call.value_start_line = token.lineno
                else:
                    call.current_value += string_value

        return self.results


def extract_godot_csharp(file_obj, keywords, comment_tags, options):
    """
    Custom C# extract to fix line numbers for Windows
    """
    with reopen_normal_read(file_obj, options.get('encoding', 'utf-8')) as f:
        data = f.read()
    extractor = CSharpExtractor(data)

    for item in extractor.get_lines_data():
        function = item['function_name']

        if function not in keywords:
            continue

        messages = [item['content']]
        yield item['line_number'], function, tuple(messages), []
