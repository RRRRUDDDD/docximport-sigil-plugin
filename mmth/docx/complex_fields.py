import re


class unknown(object):
    pass


class Hyperlink(object):
    def __init__(self, href):
        self.href = href


def hyperlink(href):
    return Hyperlink(href)


class Ruby(object):
    def __init__(self, base_text, annotation):
        self.base_text = base_text
        self.annotation = annotation


def ruby(base_text, annotation):
    return Ruby(base_text=base_text, annotation=annotation)


def parse_ruby_field_code(instruction):
    if not instruction or re.match(r"\s*EQ(?:\s|\\|$)", instruction, re.IGNORECASE) is None:
        return None

    overlay = re.search(r"\\o\s*(?:\\a[cdlr]\s*)?\(", instruction, re.IGNORECASE)
    if overlay is None:
        return None

    operands = _parenthesized_content(instruction, overlay.end() - 1)
    if operands is None:
        return None

    parts = _split_first_top_level_comma(operands)
    if parts is None:
        return None

    annotation = _read_annotation(parts[0])
    base_text = _clean_operand(parts[1])
    if not annotation or not base_text:
        return None

    return ruby(base_text=base_text, annotation=annotation)


def _read_annotation(expression):
    shift = re.search(r"\\s\s*\\up", expression, re.IGNORECASE)
    if shift is None:
        return None

    open_index = expression.find("(", shift.end())
    if open_index == -1:
        return None

    distance = expression[shift.end():open_index].strip()
    if distance and re.match(r"^-?\d+(?:\.\d+)?$", distance) is None:
        return None

    annotation = _parenthesized_content(expression, open_index)
    if annotation is None:
        return None

    if not distance:
        alternate_parts = _split_first_top_level_comma(annotation)
        if alternate_parts is not None and re.match(r"^-?\d+(?:\.\d+)?$", alternate_parts[0].strip()):
            annotation = alternate_parts[1]

    return _clean_operand(annotation)


def _parenthesized_content(value, open_index):
    if open_index >= len(value) or value[open_index] != "(":
        return None

    depth = 0
    quoted = False
    for index in range(open_index, len(value)):
        character = value[index]
        if character == '"':
            quoted = not quoted
        elif not quoted:
            if character == "(":
                depth += 1
            elif character == ")":
                depth -= 1
                if depth == 0:
                    return value[open_index + 1:index]

    return None


def _split_first_top_level_comma(value):
    depth = 0
    quoted = False
    for index, character in enumerate(value):
        if character == '"':
            quoted = not quoted
        elif not quoted:
            if character == "(":
                depth += 1
            elif character == ")":
                depth -= 1
            elif character == "," and depth == 0:
                return value[:index], value[index + 1:]

    return None


def _clean_operand(value):
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] == '"':
        return value[1:-1]
    return value
