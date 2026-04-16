import unittest

from split_blocks import markdown_to_blocks, block_to_block_type, BlockType, markdown_to_html_node


class TestMarkdownToBlocks(unittest.TestCase):

    def test_markdown_to_blocks(self):
        md = """
This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )

    def test_single_block(self):
        md = "Just a single paragraph with no blank lines."
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, ["Just a single paragraph with no blank lines."])

    def test_strips_leading_and_trailing_whitespace(self):
        # Each block should be stripped of surrounding whitespace/newlines
        md = "\n\n  Hello world  \n\n  Goodbye world  \n\n"
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, ["Hello world", "Goodbye world"])

    def test_removes_empty_blocks_from_excessive_newlines(self):
        # Three or more consecutive newlines should not produce empty blocks
        md = "First block\n\n\n\nSecond block"
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, ["First block", "Second block"])

    def test_heading_paragraph_list(self):
        md = """# This is a heading

This is a paragraph of text. It has some **bold** and _italic_ words inside of it.

- This is the first list item in a list block
- This is a list item
- This is another list item"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, [
            "# This is a heading",
            "This is a paragraph of text. It has some **bold** and _italic_ words inside of it.",
            "- This is the first list item in a list block\n- This is a list item\n- This is another list item",
        ])

    def test_empty_string(self):
        blocks = markdown_to_blocks("")
        self.assertEqual(blocks, [])

    def test_only_whitespace(self):
        blocks = markdown_to_blocks("   \n\n   \n\n   ")
        self.assertEqual(blocks, [])

    def test_last_block_is_stripped(self):
        # Specifically targets the bug where the last block is skipped in processing
        md = "First block\n\nLast block with trailing newline\n"
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, ["First block", "Last block with trailing newline"])


class TestBlockToBlockType(unittest.TestCase):

    # --- Headings ---

    def test_heading_h1(self):
        self.assertEqual(block_to_block_type("# Heading"), BlockType.HEADING)

    def test_heading_h2(self):
        self.assertEqual(block_to_block_type("## Heading"), BlockType.HEADING)

    def test_heading_h3(self):
        self.assertEqual(block_to_block_type("### Heading"), BlockType.HEADING)

    def test_heading_h6(self):
        self.assertEqual(block_to_block_type("###### Heading"), BlockType.HEADING)

    def test_heading_missing_space_is_paragraph(self):
        # '#' not followed by a space is not a valid heading
        self.assertEqual(block_to_block_type("#Heading"), BlockType.PARAGRAPH)

    def test_heading_seven_hashes_is_paragraph(self):
        # 7 '#' characters is not a valid heading
        self.assertEqual(block_to_block_type("####### Heading"), BlockType.PARAGRAPH)

    # --- Code ---

    def test_code_block(self):
        self.assertEqual(block_to_block_type("```\nsome code\n```"), BlockType.CODE)

    def test_code_block_multiline(self):
        self.assertEqual(block_to_block_type("```\nline1\nline2\n```"), BlockType.CODE)

    def test_code_missing_opening_backticks_is_paragraph(self):
        self.assertEqual(block_to_block_type("some code\n```"), BlockType.PARAGRAPH)

    def test_code_missing_closing_backticks_is_paragraph(self):
        self.assertEqual(block_to_block_type("```\nsome code"), BlockType.PARAGRAPH)

    # --- Quote ---

    def test_quote_single_line(self):
        self.assertEqual(block_to_block_type(">This is a quote"), BlockType.QUOTE)

    def test_quote_with_space_after_arrow(self):
        self.assertEqual(block_to_block_type("> This is a quote"), BlockType.QUOTE)

    def test_quote_multiline(self):
        self.assertEqual(block_to_block_type("> line one\n> line two"), BlockType.QUOTE)

    def test_quote_one_line_missing_arrow_is_paragraph(self):
        # All lines must start with '>'
        self.assertEqual(block_to_block_type("> line one\nline two"), BlockType.PARAGRAPH)

    # --- Unordered list ---

    def test_unordered_list_single_item(self):
        self.assertEqual(block_to_block_type("- item"), BlockType.UNORDERED_LIST)

    def test_unordered_list_multiple_items(self):
        self.assertEqual(block_to_block_type("- item one\n- item two\n- item three"), BlockType.UNORDERED_LIST)

    def test_unordered_list_missing_space_is_paragraph(self):
        # '-' not followed by a space is not valid
        self.assertEqual(block_to_block_type("-item"), BlockType.PARAGRAPH)

    def test_unordered_list_one_bad_line_is_paragraph(self):
        # Every line must start with '- '
        self.assertEqual(block_to_block_type("- item one\nitem two"), BlockType.PARAGRAPH)

    # --- Ordered list ---

    def test_ordered_list_single_item(self):
        self.assertEqual(block_to_block_type("1. item"), BlockType.ORDERED_LIST)

    def test_ordered_list_multiple_items(self):
        self.assertEqual(block_to_block_type("1. first\n2. second\n3. third"), BlockType.ORDERED_LIST)

    def test_ordered_list_not_starting_at_1_is_paragraph(self):
        self.assertEqual(block_to_block_type("2. second\n3. third"), BlockType.PARAGRAPH)

    def test_ordered_list_skipped_number_is_paragraph(self):
        # Numbers must increment by 1; skipping 2 is invalid
        self.assertEqual(block_to_block_type("1. first\n3. third"), BlockType.PARAGRAPH)

    # --- Paragraph ---

    def test_plain_paragraph(self):
        self.assertEqual(block_to_block_type("Just some text"), BlockType.PARAGRAPH)

    def test_paragraph_with_inline_markdown(self):
        self.assertEqual(block_to_block_type("This has **bold** and _italic_"), BlockType.PARAGRAPH)


class TestMarkdownToHtmlNode(unittest.TestCase):

    # --- From the assignment ---

    def test_paragraphs(self):
        md = """
This is **bolded** paragraph
text in a p
tag here

This is another paragraph with _italic_ text and `code` here

"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>This is <b>bolded</b> paragraph text in a p tag here</p><p>This is another paragraph with <i>italic</i> text and <code>code</code> here</p></div>",
        )

    def test_codeblock(self):
        md = """
```
This is text that _should_ remain
the **same** even with inline stuff
```
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><pre><code>This is text that _should_ remain\nthe **same** even with inline stuff\n</code></pre></div>",
        )

    # --- Headings ---

    def test_heading_h1(self):
        node = markdown_to_html_node("# Hello")
        self.assertEqual(node.to_html(), "<div><h1>Hello</h1></div>")

    def test_heading_h2(self):
        node = markdown_to_html_node("## Level Two")
        self.assertEqual(node.to_html(), "<div><h2>Level Two</h2></div>")

    def test_heading_h6(self):
        node = markdown_to_html_node("###### Six")
        self.assertEqual(node.to_html(), "<div><h6>Six</h6></div>")

    # --- Paragraph ---

    def test_simple_paragraph(self):
        node = markdown_to_html_node("Hello world")
        self.assertEqual(node.to_html(), "<div><p>Hello world</p></div>")

    def test_paragraph_with_inline_bold(self):
        node = markdown_to_html_node("This is **bold** text")
        self.assertEqual(node.to_html(), "<div><p>This is <b>bold</b> text</p></div>")

    def test_paragraph_with_inline_italic(self):
        node = markdown_to_html_node("This is _italic_ text")
        self.assertEqual(node.to_html(), "<div><p>This is <i>italic</i> text</p></div>")

    def test_paragraph_with_inline_code(self):
        node = markdown_to_html_node("Use `foo()` here")
        self.assertEqual(node.to_html(), "<div><p>Use <code>foo()</code> here</p></div>")

    # --- Quote ---

    def test_quote(self):
        node = markdown_to_html_node("> This is a quote")
        self.assertEqual(node.to_html(), "<div><blockquote>This is a quote</blockquote></div>")

    # --- Unordered list ---

    def test_unordered_list(self):
        node = markdown_to_html_node("- item one\n- item two")
        self.assertEqual(node.to_html(), "<div><ul><li>item one</li><li>item two</li></ul></div>")

    # --- Ordered list ---

    def test_ordered_list(self):
        node = markdown_to_html_node("1. first\n2. second\n3. third")
        self.assertEqual(node.to_html(), "<div><ol><li>first</li><li>second</li><li>third</li></ol></div>")

    # --- Multiple blocks ---

    def test_heading_and_paragraph(self):
        md = "# Title\n\nSome paragraph text"
        node = markdown_to_html_node(md)
        self.assertEqual(node.to_html(), "<div><h1>Title</h1><p>Some paragraph text</p></div>")

    def test_all_block_types(self):
        md = "# Title\n\nA paragraph\n\n- item one\n- item two"
        node = markdown_to_html_node(md)
        self.assertEqual(node.to_html(), "<div><h1>Title</h1><p>A paragraph</p><ul><li>item one</li><li>item two</li></ul></div>")

    # --- Inline markdown inside blocks ---

    def test_heading_with_inline_bold(self):
        # heading strip must not eat the space before "title"
        node = markdown_to_html_node("# **bold** title")
        self.assertEqual(node.to_html(), "<div><h1><b>bold</b> title</h1></div>")

    def test_unordered_list_with_inline(self):
        # strip must not eat the space after inline elements in list items
        node = markdown_to_html_node("- **bold** item\n- _italic_ item")
        self.assertEqual(node.to_html(), "<div><ul><li><b>bold</b> item</li><li><i>italic</i> item</li></ul></div>")

    def test_ordered_list_with_inline(self):
        node = markdown_to_html_node("1. **first** item\n2. _second_ item")
        self.assertEqual(node.to_html(), "<div><ol><li><b>first</b> item</li><li><i>second</i> item</li></ol></div>")

    def test_multiline_quote(self):
        node = markdown_to_html_node("> line one\n> line two")
        self.assertEqual(node.to_html(), "<div><blockquote>line one\nline two</blockquote></div>")

    # --- Links and images in paragraphs ---

    def test_paragraph_with_link(self):
        node = markdown_to_html_node("Visit [google](https://google.com) today")
        self.assertEqual(node.to_html(), '<div><p>Visit <a href="https://google.com">google</a> today</p></div>')

    def test_paragraph_with_image(self):
        node = markdown_to_html_node("See ![cat](https://example.com/cat.png) here")
        self.assertEqual(node.to_html(), '<div><p>See <img src="https://example.com/cat.png" alt="cat"> here</p></div>')

    def test_heading_with_inline_code(self):
        # space between heading text and inline element must be preserved
        node = markdown_to_html_node("# Use `foo()`")
        self.assertEqual(node.to_html(), "<div><h1>Use <code>foo()</code></h1></div>")

    def test_quote_without_space_after_arrow(self):
        # '>' without a space is valid per the spec
        node = markdown_to_html_node(">no space quote")
        self.assertEqual(node.to_html(), "<div><blockquote>no space quote</blockquote></div>")

    def test_image_in_list_item(self):
        node = markdown_to_html_node("- see ![cat](https://example.com/cat.png)")
        self.assertEqual(node.to_html(), '<div><ul><li>see <img src="https://example.com/cat.png" alt="cat"></li></ul></div>')


if __name__ == "__main__":
    unittest.main()
