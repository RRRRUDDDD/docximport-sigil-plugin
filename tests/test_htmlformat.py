# coding=utf-8

from __future__ import unicode_literals

import re
import sys
import types
import unittest


sys.modules.setdefault("regex", re)
sys.modules.setdefault(
    "sigil_gumbo_bs4_adapter",
    types.ModuleType("sigil_gumbo_bs4_adapter"),
)

_normalise_blank_paragraphs = __import__(
    "htmlformat"
)._normalise_blank_paragraphs


class BlankParagraphTests(unittest.TestCase):
    def test_empty_paragraph_with_attributes_becomes_a_break(self):
        self.assertEqual(
            '<br/>',
            _normalise_blank_paragraphs(
                '<p style="font-size: 10.5pt"></p>'
            ),
        )

    def test_whitespace_and_nbsp_only_paragraphs_become_breaks(self):
        fragment = (
            '<p> \n&#160;\t</p>'
            '<p>&#xA0;</p>'
            '<p>&nbsp;</p>'
            '<p>\u00a0</p>'
        )

        self.assertEqual(
            '<br/><br/><br/><br/>',
            _normalise_blank_paragraphs(fragment),
        )

    def test_nbsp_next_to_text_is_not_replaced(self):
        fragment = '<p>&#160;正文</p><p>正文&#160;</p>'

        self.assertEqual(fragment, _normalise_blank_paragraphs(fragment))


if __name__ == "__main__":
    unittest.main()
