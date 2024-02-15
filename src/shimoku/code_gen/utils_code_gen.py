
def code_gen_from_value(v):
    if isinstance(v, str):
        special_chars = [
            '"', "'", '\\', '\n', '\t', '\r', '\b', '\f', '\v',
            '\a', '\0', '\1', '\2', '\3', '\4', '\5', '\6', '\7'
        ]
        replacement_chars = [
            '\"', "\'", '\\\\', '\\n', '\\t', '\\r', '\\b', '\\f', '\\v',
            '\\a', '\\0', '\\1', '\\2', '\\3', '\\4', '\\5', '\\6', '\\7'
        ]
        result = ''
        for char in v:
            if char in special_chars:
                result += replacement_chars[special_chars.index(char)]
            else:
                result += char
        print(result) if any(char in special_chars for char in v) else None
        return f'"{result}"'
    return v


def code_gen_from_list(l, deep=0):
    return [' ' * deep + str(l) + ',']
    # code_lines = [' ' * deep + '[']
    # deep += 4
    # for element in l:
    #     if isinstance(element, dict):
    #         code_lines.extend(self._code_gen_from_dict(element, deep))
    #     elif isinstance(element, list):
    #         code_lines.extend(self._code_gen_from_list(element, deep))
    #     else:
    #         code_lines.append(' ' * deep + f'{self._code_gen_value(element)},')
    # deep -= 4
    # code_lines.append(' ' * deep + '],')
    # return code_lines


def code_gen_from_dict(d, deep=0):
    return [' ' * deep + str(d) + ',']
    # code_lines = [' ' * deep + '{']
    # deep += 4
    # for k, v in d.items():
    #     if isinstance(v, (dict, list)):
    #         code_lines.append(' ' * deep + f'"{k}":')
    #         if isinstance(v, dict):
    #             code_lines.extend(self._code_gen_from_dict(v, deep))
    #         elif isinstance(v, list):
    #             code_lines.extend(self._code_gen_from_list(v, deep))
    #     else:
    #         code_lines.append(' ' * deep + f'"{k}": ' + f'{self._code_gen_value(v)},')
    # deep -= 4
    # code_lines.append(' ' * deep + '},')
    # return code_lines
