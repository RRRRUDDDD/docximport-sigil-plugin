import collections


class Styles(object):
    @staticmethod
    def create(paragraph_styles=None, character_styles=None, table_styles=None, numbering_styles=None, default_font_size=None):
        if paragraph_styles is None:
            paragraph_styles = {}
        if character_styles is None:
            character_styles = {}
        if table_styles is None:
            table_styles = {}
        if numbering_styles is None:
            numbering_styles = {}

        return Styles(
            paragraph_styles=paragraph_styles,
            character_styles=character_styles,
            table_styles=table_styles,
            numbering_styles=numbering_styles,
            default_font_size=default_font_size,
        )

    def __init__(self, paragraph_styles, character_styles, table_styles, numbering_styles, default_font_size=None):
        self._paragraph_styles = paragraph_styles
        self._character_styles = character_styles
        self._table_styles = table_styles
        self._numbering_styles = numbering_styles
        self._default_font_size = default_font_size

    def find_paragraph_style_by_id(self, style_id):
        return self._paragraph_styles.get(style_id)

    def find_character_style_by_id(self, style_id):
        return self._character_styles.get(style_id)

    def find_table_style_by_id(self, style_id):
        return self._table_styles.get(style_id)

    def find_numbering_style_by_id(self, style_id):
        return self._numbering_styles.get(style_id)

    def find_paragraph_style_font_size_by_id(self, style_id):
        return _find_style_font_size(
            self._paragraph_styles,
            style_id,
            fallback=self._default_font_size,
        )

    def find_character_style_font_size_by_id(self, style_id):
        return _find_style_font_size(
            self._character_styles,
            style_id,
            fallback=None,
        )


Styles.EMPTY = Styles(
    paragraph_styles={},
    character_styles={},
    table_styles={},
    numbering_styles={},
    default_font_size=None,
)


def read_styles_xml_element(element):
    paragraph_styles = {}
    character_styles = {}
    table_styles = {}
    numbering_styles = {}
    styles = {
        "paragraph": paragraph_styles,
        "character": character_styles,
        "table": table_styles,
    }
    default_font_size = _read_font_size(
        element
            .find_child_or_null("w:docDefaults")
            .find_child_or_null("w:rPrDefault")
            .find_child_or_null("w:rPr")
    )

    for style_element in element.find_children("w:style"):
        style = _read_style_element(style_element)
        element_type = style_element.attributes["w:type"]
        if element_type == "numbering":
            numbering_styles[style.style_id] = _read_numbering_style_element(style_element)
        else:
            style_set = styles.get(element_type)
            if style_set is not None:
                style_set[style.style_id] = style

    return Styles(
        paragraph_styles=paragraph_styles,
        character_styles=character_styles,
        table_styles=table_styles,
        numbering_styles=numbering_styles,
        default_font_size=default_font_size,
    )


class Style(collections.namedtuple("StyleBase", ["style_id", "name", "font_size", "based_on"])):
    __slots__ = ()

    def __new__(cls, style_id, name, font_size=None, based_on=None):
        return super(Style, cls).__new__(cls, style_id, name, font_size, based_on)


def _read_style_element(element):
    style_id = element.attributes["w:styleId"]
    name = element.find_child_or_null("w:name").attributes.get("w:val")
    font_size = _read_font_size(element.find_child_or_null("w:rPr"))
    based_on = element.find_child_or_null("w:basedOn").attributes.get("w:val")
    return Style(
        style_id=style_id,
        name=name,
        font_size=font_size,
        based_on=based_on,
    )


def _find_style_font_size(style_set, style_id, fallback):
    seen = set()
    while style_id is not None and style_id not in seen:
        seen.add(style_id)
        style = style_set.get(style_id)
        if style is None:
            break
        if style.font_size is not None:
            return style.font_size
        style_id = style.based_on

    return fallback


def _read_font_size(properties):
    for element_name in ["w:sz", "w:szCs"]:
        value = properties.find_child_or_null(element_name).attributes.get("w:val")
        try:
            half_points = int(value)
        except (TypeError, ValueError):
            continue
        if half_points > 0:
            return half_points / 2.0

    return None


NumberingStyle = collections.namedtuple("NumberingStyle", ["num_id"])


def _read_numbering_style_element(element):
    num_id = element \
        .find_child_or_null("w:pPr") \
        .find_child_or_null("w:numPr") \
        .find_child_or_null("w:numId") \
        .attributes.get("w:val")

    return NumberingStyle(num_id=num_id)
