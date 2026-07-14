# coding=utf-8

from __future__ import unicode_literals

import unittest

from mmth import conversion, document_matchers, documents, html_paths, styles
from mmth.docx import body_xml, complex_fields, styles_xml
from mmth.docx.xmlparser import element, text


def _run(*children):
    return element("w:r", children=list(children))


def _text_run(value):
    return _run(element("w:t", children=[text(value)]))


def _formatted_text_run(value, *properties):
    return _run(
        element("w:rPr", children=list(properties)),
        element("w:t", children=[text(value)]),
    )


def _field_char(field_char_type):
    return element("w:fldChar", {"w:fldCharType": field_char_type})


def _instruction(value):
    return element("w:instrText", children=[text(value)])


def _native_ruby(base_children, annotation):
    return element("w:ruby", children=[
        element("w:rubyPr"),
        element("w:rt", children=[_text_run(annotation)]),
        element("w:rubyBase", children=list(base_children)),
    ])


def _convert_paragraph(children, properties=None, word_styles=None):
    paragraph_children = []
    if properties is not None:
        paragraph_children.append(properties)
    paragraph_children.extend(children)

    read_result = body_xml.reader(styles=word_styles).read_all([
        element("w:p", children=paragraph_children),
    ])
    document = documents.document(read_result.value)
    return conversion.convert_document_element_to_html(
        document,
        output_format="html",
        ignore_empty_paragraphs=False,
    ).value


class WordAlignmentTests(unittest.TestCase):
    def test_right_aligned_paragraph_uses_inline_text_alignment(self):
        properties = element("w:pPr", children=[
            element("w:jc", {"w:val": "right"}),
        ])

        html = _convert_paragraph([_text_run("靠右")], properties)

        self.assertEqual('<p style="text-align: right">靠右</p>', html)

    def test_alignment_does_not_mutate_a_shared_style_map_path(self):
        mapped_path = html_paths.path([
            html_paths.element("div", class_names=["mapped"]),
            html_paths.element("p", fresh=True),
        ])
        style_map = [styles.style(document_matchers.paragraph(), mapped_path)]
        document = documents.document([
            documents.paragraph([documents.text("右")], alignment="right"),
            documents.paragraph([documents.text("左")], alignment="left"),
        ])

        html = conversion.convert_document_element_to_html(
            document,
            style_map=style_map,
            output_format="html",
        ).value

        self.assertEqual(
            '<div class="mapped"><p style="text-align: right">右</p>'
            '<p>左</p></div>',
            html,
        )

    def test_right_alignment_respects_an_ignored_style_map_path(self):
        style_map = [
            styles.style(document_matchers.paragraph(), html_paths.ignore),
        ]
        document = documents.document([
            documents.paragraph([documents.text("忽略")], alignment="right"),
        ])

        html = conversion.convert_document_element_to_html(
            document,
            style_map=style_map,
            output_format="html",
        ).value

        self.assertEqual("", html)


class RubyFieldTests(unittest.TestCase):
    def test_complex_eq_field_is_converted_to_ruby_and_fallback_is_suppressed(self):
        html = _convert_paragraph([
            _run(_field_char("begin")),
            _run(_instruction(
                r' EQ \* jc2 \* "Font:Yu Mincho" \* hps10 '
                r'\o\ad(\s\up 9(かんじ),漢字) '
            )),
            _run(_field_char("separate")),
            _text_run("かんじ漢字"),
            _run(_field_char("end")),
        ])

        self.assertEqual('<p><ruby>漢字<rt>かんじ</rt></ruby></p>', html)

    def test_simple_eq_field_is_converted_to_ruby(self):
        simple_field = element("w:fldSimple", {
            "w:instr": r'EQ \o\ad(\s\up 9(han),漢)',
        }, children=[_text_run("han漢")])

        html = _convert_paragraph([simple_field])

        self.assertEqual('<p><ruby>漢<rt>han</rt></ruby></p>', html)

    def test_parser_preserves_nested_parentheses_and_commas(self):
        ruby = complex_fields.parse_ruby_field_code(
            r'EQ \o\ad(\s\up 9(かん(じ),かな),漢字,語)'
        )

        self.assertIsInstance(ruby, complex_fields.Ruby)
        self.assertEqual("漢字,語", ruby.base_text)
        self.assertEqual("かん(じ),かな", ruby.annotation)

    def test_parser_preserves_an_apostrophe_in_the_annotation(self):
        ruby = complex_fields.parse_ruby_field_code(
            r"EQ \o\ad(\s\up 9(Xi'an),西安)"
        )

        self.assertIsInstance(ruby, complex_fields.Ruby)
        self.assertEqual("西安", ruby.base_text)
        self.assertEqual("Xi'an", ruby.annotation)

    def test_parser_accepts_word_overlay_alignment_variants(self):
        for alignment in ["ad", "ac", "al", "ar"]:
            ruby = complex_fields.parse_ruby_field_code(
                r'EQ \o\{0}(\s\up 9(かんじ),漢字)'.format(alignment)
            )

            self.assertIsInstance(ruby, complex_fields.Ruby)
            self.assertEqual("漢字", ruby.base_text)
            self.assertEqual("かんじ", ruby.annotation)

    def test_ruby_nested_in_a_hyperlink_keeps_the_link(self):
        html = _convert_paragraph([
            _run(_field_char("begin")),
            _run(_instruction(r' HYPERLINK "https://example.com" ')),
            _run(_field_char("separate")),
            _run(_field_char("begin")),
            _run(_instruction(r'EQ \o\ad(\s\up 9(かんじ),漢字)')),
            _run(_field_char("separate")),
            _text_run("かんじ漢字"),
            _run(_field_char("end")),
            _run(_field_char("end")),
        ])

        self.assertEqual(
            '<p><a href="https://example.com"><ruby>漢字<rt>かんじ</rt>'
            '</ruby></a></p>',
            html,
        )

    def test_native_ruby_in_a_complex_hyperlink_keeps_one_link(self):
        html = _convert_paragraph([
            _run(_field_char("begin")),
            _run(_instruction(r' HYPERLINK "https://example.com" ')),
            _run(_field_char("separate")),
            _run(_native_ruby([_text_run("漢")], "かん")),
            _run(_field_char("end")),
        ])

        self.assertEqual(
            '<p><a href="https://example.com"><ruby>漢<rt>かん</rt>'
            '</ruby></a></p>',
            html,
        )

    def test_non_ruby_complex_field_keeps_displayed_result(self):
        html = _convert_paragraph([
            _run(_field_char("begin")),
            _run(_instruction(" DATE ")),
            _run(_field_char("separate")),
            _text_run("2026-07-14"),
            _run(_field_char("end")),
        ])

        self.assertEqual('<p>2026-07-14</p>', html)

    def test_malformed_eq_field_keeps_displayed_result(self):
        html = _convert_paragraph([
            _run(_field_char("begin")),
            _run(_instruction(r'EQ \o\ad(缺少注音)')),
            _run(_field_char("separate")),
            _text_run("原文"),
            _run(_field_char("end")),
        ])

        self.assertEqual('<p>原文</p>', html)


class SuperscriptAndFontSizeTests(unittest.TestCase):
    def test_unseparated_eq_fields_and_native_ruby_keep_emphasised_text(self):
        def eq_emphasis(base_text):
            return [
                _run(_field_char("begin")),
                _run(_instruction(
                    r'EQ \* jc0 \* "Font:宋体" \* hps16 '
                    r'\o(\s\up 9(•),{0})'.format(base_text)
                )),
                _run(_field_char("end")),
            ]

        children = [_text_run("我竟然真的体会到了那")]
        children.extend(eq_emphasis("无"))
        children.extend([
            _run(_native_ruby([_text_run("法")], "•")),
            _run(_native_ruby([_text_run("想")], "•")),
        ])
        children.extend(eq_emphasis("象"))
        children.extend([
            _run(_native_ruby([_text_run("的")], "•")),
            _run(_native_ruby([_text_run("初")], "•")),
            _run(_native_ruby([_text_run("恋")], "•")),
            _text_run("。"),
        ])

        html = _convert_paragraph(children)

        self.assertEqual(
            '<p>我竟然真的体会到了那'
            '<ruby>无<rt>•</rt></ruby>'
            '<ruby>法<rt>•</rt></ruby>'
            '<ruby>想<rt>•</rt></ruby>'
            '<ruby>象<rt>•</rt></ruby>'
            '<ruby>的<rt>•</rt></ruby>'
            '<ruby>初<rt>•</rt></ruby>'
            '<ruby>恋<rt>•</rt></ruby>。</p>',
            html,
        )

    def test_native_ruby_preserves_base_run_formatting(self):
        html = _convert_paragraph([
            _run(_native_ruby([
                _formatted_text_run("法", element("w:b")),
            ], "•")),
        ])

        self.assertEqual(
            '<p><ruby><strong>法</strong><rt>•</rt></ruby></p>',
            html,
        )

    def test_superscript_and_following_text_are_preserved(self):
        html = _convert_paragraph([
            _text_run("平方"),
            _formatted_text_run(
                "2",
                element("w:vertAlign", {"w:val": "superscript"}),
            ),
            _text_run("之后"),
        ])

        self.assertEqual('<p>平方<sup>2</sup>之后</p>', html)

    def test_ruby_overlay_variant_does_not_eat_base_or_following_text(self):
        html = _convert_paragraph([
            _run(_field_char("begin")),
            _run(_instruction(r'EQ \o\ac(\s\up 9(かんじ),漢字)')),
            _run(_field_char("separate")),
            _run(_field_char("end")),
            _formatted_text_run(
                "2",
                element("w:vertAlign", {"w:val": "superscript"}),
            ),
            _text_run("之后"),
        ])

        self.assertEqual(
            '<p><ruby>漢字<rt>かんじ</rt></ruby><sup>2</sup>之后</p>',
            html,
        )

    def test_word_half_point_font_size_is_preserved(self):
        html = _convert_paragraph([
            _formatted_text_run("字号", element("w:sz", {"w:val": "21"})),
        ])

        self.assertEqual(
            '<p><span style="font-size: 10.5pt">字号</span></p>',
            html,
        )

    def test_complex_script_font_size_is_used_as_a_fallback(self):
        html = _convert_paragraph([
            _formatted_text_run("字号", element("w:szCs", {"w:val": "24"})),
        ])

        self.assertEqual(
            '<p><span style="font-size: 12pt">字号</span></p>',
            html,
        )

    def test_font_size_wraps_superscript_without_losing_it(self):
        html = _convert_paragraph([
            _formatted_text_run(
                "2",
                element("w:vertAlign", {"w:val": "superscript"}),
                element("w:sz", {"w:val": "24"}),
            ),
        ])

        self.assertEqual(
            '<p><span style="font-size: 12pt"><sup>2</sup></span></p>',
            html,
        )

    def test_paragraph_style_inherits_its_font_size(self):
        word_styles = styles_xml.read_styles_xml_element(element(
            "w:styles",
            children=[
                element("w:style", {
                    "w:type": "paragraph",
                    "w:styleId": "Base",
                }, children=[
                    element("w:name", {"w:val": "Base"}),
                    element("w:rPr", children=[
                        element("w:sz", {"w:val": "28"}),
                    ]),
                ]),
                element("w:style", {
                    "w:type": "paragraph",
                    "w:styleId": "Child",
                }, children=[
                    element("w:name", {"w:val": "Child"}),
                    element("w:basedOn", {"w:val": "Base"}),
                ]),
            ],
        ))
        properties = element("w:pPr", children=[
            element("w:pStyle", {"w:val": "Child"}),
        ])

        html = _convert_paragraph(
            [_text_run("样式字号")],
            properties,
            word_styles=word_styles,
        )

        self.assertEqual('<p style="font-size: 14pt">样式字号</p>', html)

    def test_document_default_font_size_is_preserved(self):
        word_styles = styles_xml.read_styles_xml_element(element(
            "w:styles",
            children=[
                element("w:docDefaults", children=[
                    element("w:rPrDefault", children=[
                        element("w:rPr", children=[
                            element("w:sz", {"w:val": "22"}),
                        ]),
                    ]),
                ]),
            ],
        ))

        html = _convert_paragraph(
            [_text_run("默认字号")],
            word_styles=word_styles,
        )

        self.assertEqual('<p style="font-size: 11pt">默认字号</p>', html)

    def test_character_style_font_size_is_preserved(self):
        word_styles = styles_xml.read_styles_xml_element(element(
            "w:styles",
            children=[
                element("w:style", {
                    "w:type": "character",
                    "w:styleId": "SmallText",
                }, children=[
                    element("w:name", {"w:val": "Small Text"}),
                    element("w:rPr", children=[
                        element("w:sz", {"w:val": "18"}),
                    ]),
                ]),
            ],
        ))

        html = _convert_paragraph([
            _formatted_text_run(
                "字符样式",
                element("w:rStyle", {"w:val": "SmallText"}),
            ),
        ], word_styles=word_styles)

        self.assertEqual(
            '<p><span style="font-size: 9pt">字符样式</span></p>',
            html,
        )


if __name__ == "__main__":
    unittest.main()
