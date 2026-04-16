import unittest

from textnode import TextNode, TextType
from split_nodes import split_nodes_delimiter, extract_markdown_images, extract_markdown_links, split_nodes_image, split_nodes_link, text_to_textnodes


class TestSplitNodesDelimiter(unittest.TestCase):

    # --- Basic splitting ---

    def test_split_code(self):
        node = TextNode("This is text with a `code block` word", TextType.TEXT)
        result = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(result, [
            TextNode("This is text with a ", TextType.TEXT),
            TextNode("code block", TextType.CODE),
            TextNode(" word", TextType.TEXT),
        ])

    def test_split_bold(self):
        node = TextNode("This is text with a **bolded phrase** in the middle", TextType.TEXT)
        result = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertEqual(result, [
            TextNode("This is text with a ", TextType.TEXT),
            TextNode("bolded phrase", TextType.BOLD),
            TextNode(" in the middle", TextType.TEXT),
        ])

    def test_split_italic(self):
        node = TextNode("This is _italic_ text", TextType.TEXT)
        result = split_nodes_delimiter([node], "_", TextType.ITALIC)
        self.assertEqual(result, [
            TextNode("This is ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" text", TextType.TEXT),
        ])

    # --- Non-TEXT nodes pass through unchanged ---

    def test_non_text_node_passes_through(self):
        node = TextNode("already bold", TextType.BOLD)
        result = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertEqual(result, [TextNode("already bold", TextType.BOLD)])

    def test_mixed_list_non_text_unchanged(self):
        bold_node = TextNode("bold", TextType.BOLD)
        text_node = TextNode("hello `code` world", TextType.TEXT)
        result = split_nodes_delimiter([bold_node, text_node], "`", TextType.CODE)
        self.assertEqual(result, [
            TextNode("bold", TextType.BOLD),
            TextNode("hello ", TextType.TEXT),
            TextNode("code", TextType.CODE),
            TextNode(" world", TextType.TEXT),
        ])

    # --- Multiple nodes in input ---

    def test_multiple_text_nodes(self):
        node1 = TextNode("Hello `foo` world", TextType.TEXT)
        node2 = TextNode("Another `bar` here", TextType.TEXT)
        result = split_nodes_delimiter([node1, node2], "`", TextType.CODE)
        self.assertEqual(result, [
            TextNode("Hello ", TextType.TEXT),
            TextNode("foo", TextType.CODE),
            TextNode(" world", TextType.TEXT),
            TextNode("Another ", TextType.TEXT),
            TextNode("bar", TextType.CODE),
            TextNode(" here", TextType.TEXT),
        ])

    # --- Multiple delimiters pairs in input ---

    def test_two_bold_pairs(self):
        node = TextNode("This is **bold1** and **bold2** text", TextType.TEXT)
        result = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertEqual(result, [
            TextNode("This is ", TextType.TEXT),
            TextNode("bold1", TextType.BOLD),
            TextNode(" and ", TextType.TEXT),
            TextNode("bold2", TextType.BOLD),
            TextNode(" text", TextType.TEXT),
        ])

    def test_two_code_pairs(self):
        node = TextNode("Use `foo()` and `bar()` together", TextType.TEXT)
        result = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(result, [
            TextNode("Use ", TextType.TEXT),
            TextNode("foo()", TextType.CODE),
            TextNode(" and ", TextType.TEXT),
            TextNode("bar()", TextType.CODE),
            TextNode(" together", TextType.TEXT),
        ])

    def test_three_italic_pairs(self):
        node = TextNode("_a_ then _b_ then _c_", TextType.TEXT)
        result = split_nodes_delimiter([node], "_", TextType.ITALIC)
        self.assertEqual(result, [
            TextNode("", TextType.TEXT),
            TextNode("a", TextType.ITALIC),
            TextNode(" then ", TextType.TEXT),
            TextNode("b", TextType.ITALIC),
            TextNode(" then ", TextType.TEXT),
            TextNode("c", TextType.ITALIC),
            TextNode("", TextType.TEXT),
        ])

    # --- Edge cases ---

    def test_delimiter_at_start(self):
        node = TextNode("`code` at the start", TextType.TEXT)
        result = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(result, [
            TextNode("", TextType.TEXT),
            TextNode("code", TextType.CODE),
            TextNode(" at the start", TextType.TEXT),
        ])

    def test_delimiter_at_end(self):
        node = TextNode("text at the end `code`", TextType.TEXT)
        result = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(result, [
            TextNode("text at the end ", TextType.TEXT),
            TextNode("code", TextType.CODE),
            TextNode("", TextType.TEXT),
        ])

    def test_no_delimiter_in_text(self):
        node = TextNode("plain text no delimiter", TextType.TEXT)
        result = split_nodes_delimiter([node], "`", TextType.CODE)
        # No delimiter found — should either return node as-is or raise. Adjust to match your behaviour.
        self.assertEqual(result, [TextNode("plain text no delimiter", TextType.TEXT)])

    # --- Invalid markdown ---

    def test_missing_closing_delimiter_raises(self):
        node = TextNode("This is `unclosed code", TextType.TEXT)
        with self.assertRaises(Exception):
            split_nodes_delimiter([node], "`", TextType.CODE)


class TestExtractMarkdownImages(unittest.TestCase):

    def test_extract_two_images(self):
        text = "This is text with a ![rick roll](https://i.imgur.com/aKaOqIh.gif) and ![obi wan](https://i.imgur.com/fJRm4Vk.jpeg)"
        result = extract_markdown_images(text)
        self.assertEqual(result, [
            ("rick roll", "https://i.imgur.com/aKaOqIh.gif"),
            ("obi wan", "https://i.imgur.com/fJRm4Vk.jpeg"),
        ])

    def test_no_images(self):
        text = "This is plain text with no images"
        result = extract_markdown_images(text)
        self.assertEqual(result, [])

    def test_does_not_match_plain_links(self):
        text = "This is a [link](https://example.com) not an image"
        result = extract_markdown_images(text)
        self.assertEqual(result, [])

    def test_single_image(self):
        text = "Look at this: ![cat](https://example.com/cat.png)"
        result = extract_markdown_images(text)
        self.assertEqual(result, [("cat", "https://example.com/cat.png")])


class TestExtractMarkdownLinks(unittest.TestCase):

    def test_extract_two_links(self):
        text = "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)"
        result = extract_markdown_links(text)
        self.assertEqual(result, [
            ("to boot dev", "https://www.boot.dev"),
            ("to youtube", "https://www.youtube.com/@bootdotdev"),
        ])

    def test_no_links(self):
        text = "This is plain text with no links"
        result = extract_markdown_links(text)
        self.assertEqual(result, [])

    def test_single_link(self):
        text = "Visit [Google](https://www.google.com)"
        result = extract_markdown_links(text)
        self.assertEqual(result, [("Google", "https://www.google.com")])

    def test_also_matches_images(self):
        # extract_markdown_links regex matches image syntax too (no leading !)
        text = "![alt](https://img.com/a.png) and [link](https://example.com)"
        result = extract_markdown_links(text)
        self.assertIn(("link", "https://example.com"), result)


class TestSplitNodesImage(unittest.TestCase):

    def test_split_images(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.TEXT),
                TextNode("second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"),
            ],
            new_nodes,
        )

    def test_single_image(self):
        node = TextNode("Look at ![cat](https://example.com/cat.png) here", TextType.TEXT)
        result = split_nodes_image([node])
        self.assertEqual(result, [
            TextNode("Look at ", TextType.TEXT),
            TextNode("cat", TextType.IMAGE, "https://example.com/cat.png"),
            TextNode(" here", TextType.TEXT),
        ])

    def test_image_at_start(self):
        node = TextNode("![cat](https://example.com/cat.png) some text", TextType.TEXT)
        result = split_nodes_image([node])
        self.assertEqual(result, [
            TextNode("cat", TextType.IMAGE, "https://example.com/cat.png"),
            TextNode(" some text", TextType.TEXT),
        ])

    def test_image_at_end(self):
        node = TextNode("some text ![cat](https://example.com/cat.png)", TextType.TEXT)
        result = split_nodes_image([node])
        self.assertEqual(result, [
            TextNode("some text ", TextType.TEXT),
            TextNode("cat", TextType.IMAGE, "https://example.com/cat.png"),
        ])

    def test_no_images(self):
        node = TextNode("plain text with no images", TextType.TEXT)
        result = split_nodes_image([node])
        self.assertEqual(result, [TextNode("plain text with no images", TextType.TEXT)])

    def test_non_text_node_passes_through(self):
        node = TextNode("already bold", TextType.BOLD)
        result = split_nodes_image([node])
        self.assertEqual(result, [TextNode("already bold", TextType.BOLD)])

    def test_text_with_bang_and_image(self):
        node = TextNode("Hello! Look at ![cat](https://example.com/cat.png) wow!", TextType.TEXT)
        result = split_nodes_image([node])
        self.assertEqual(result, [
            TextNode("Hello! Look at ", TextType.TEXT),
            TextNode("cat", TextType.IMAGE, "https://example.com/cat.png"),
            TextNode(" wow!", TextType.TEXT),
        ])
    
    def test_multiple_nodes(self):
        node1 = TextNode("See ![dog](https://example.com/dog.png) here", TextType.TEXT)
        node2 = TextNode("And ![cat](https://example.com/cat.png) there", TextType.TEXT)
        result = split_nodes_image([node1, node2])
        self.assertEqual(result, [
            TextNode("See ", TextType.TEXT),
            TextNode("dog", TextType.IMAGE, "https://example.com/dog.png"),
            TextNode(" here", TextType.TEXT),
            TextNode("And ", TextType.TEXT),
            TextNode("cat", TextType.IMAGE, "https://example.com/cat.png"),
            TextNode(" there", TextType.TEXT),
        ])

    def test_mixed_node_types(self):
        bold_node = TextNode("bold text", TextType.BOLD)
        text_node = TextNode("Look at ![cat](https://example.com/cat.png) wow", TextType.TEXT)
        result = split_nodes_image([bold_node, text_node])
        self.assertEqual(result, [
            TextNode("bold text", TextType.BOLD),
            TextNode("Look at ", TextType.TEXT),
            TextNode("cat", TextType.IMAGE, "https://example.com/cat.png"),
            TextNode(" wow", TextType.TEXT),
        ])

    def test_image_and_link_in_same_node(self):
        # split_nodes_image should only extract images; link markdown stays as raw text
        node = TextNode(
            "See ![cat](https://example.com/cat.png) and [google](https://google.com)",
            TextType.TEXT,
        )
        result = split_nodes_image([node])
        self.assertEqual(result, [
            TextNode("See ", TextType.TEXT),
            TextNode("cat", TextType.IMAGE, "https://example.com/cat.png"),
            TextNode(" and [google](https://google.com)", TextType.TEXT),
        ])

class TestSplitNodesLink(unittest.TestCase):

    def test_split_links(self):
        node = TextNode(
            "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("This is text with a link ", TextType.TEXT),
                TextNode("to boot dev", TextType.LINK, "https://www.boot.dev"),
                TextNode(" and ", TextType.TEXT),
                TextNode("to youtube", TextType.LINK, "https://www.youtube.com/@bootdotdev"),
            ],
            new_nodes,
        )

    def test_single_link(self):
        node = TextNode("Visit [Google](https://www.google.com) today", TextType.TEXT)
        result = split_nodes_link([node])
        self.assertEqual(result, [
            TextNode("Visit ", TextType.TEXT),
            TextNode("Google", TextType.LINK, "https://www.google.com"),
            TextNode(" today", TextType.TEXT),
        ])

    def test_link_at_start(self):
        node = TextNode("[Google](https://www.google.com) is a search engine", TextType.TEXT)
        result = split_nodes_link([node])
        self.assertEqual(result, [
            TextNode("Google", TextType.LINK, "https://www.google.com"),
            TextNode(" is a search engine", TextType.TEXT),
        ])

    def test_link_at_end(self):
        node = TextNode("Check out [Google](https://www.google.com)", TextType.TEXT)
        result = split_nodes_link([node])
        self.assertEqual(result, [
            TextNode("Check out ", TextType.TEXT),
            TextNode("Google", TextType.LINK, "https://www.google.com"),
        ])

    def test_no_links(self):
        node = TextNode("plain text with no links", TextType.TEXT)
        result = split_nodes_link([node])
        self.assertEqual(result, [TextNode("plain text with no links", TextType.TEXT)])

    def test_non_text_node_passes_through(self):
        node = TextNode("already bold", TextType.BOLD)
        result = split_nodes_link([node])
        self.assertEqual(result, [TextNode("already bold", TextType.BOLD)])

    def test_multiple_nodes(self):
        node1 = TextNode("Visit [Google](https://www.google.com) now", TextType.TEXT)
        node2 = TextNode("Or [Bing](https://www.bing.com) instead", TextType.TEXT)
        result = split_nodes_link([node1, node2])
        self.assertEqual(result, [
            TextNode("Visit ", TextType.TEXT),
            TextNode("Google", TextType.LINK, "https://www.google.com"),
            TextNode(" now", TextType.TEXT),
            TextNode("Or ", TextType.TEXT),
            TextNode("Bing", TextType.LINK, "https://www.bing.com"),
            TextNode(" instead", TextType.TEXT),
        ])

    def test_mixed_node_types(self):
        italic_node = TextNode("italic text", TextType.ITALIC)
        text_node = TextNode("Check [Google](https://www.google.com) out", TextType.TEXT)
        result = split_nodes_link([italic_node, text_node])
        self.assertEqual(result, [
            TextNode("italic text", TextType.ITALIC),
            TextNode("Check ", TextType.TEXT),
            TextNode("Google", TextType.LINK, "https://www.google.com"),
            TextNode(" out", TextType.TEXT),
        ])

    def test_link_and_image_in_same_node(self):
        # split_nodes_link should only extract links; image markdown stays as raw text
        node = TextNode(
            "[google](https://google.com) and ![cat](https://example.com/cat.png)",
            TextType.TEXT,
        )
        result = split_nodes_link([node])
        self.assertEqual(result, [
            TextNode("google", TextType.LINK, "https://google.com"),
            TextNode(" and ![cat](https://example.com/cat.png)", TextType.TEXT),
        ])


class TestTextToTextNodes(unittest.TestCase):

    def test_full_example_from_assignment(self):
        text = "This is **text** with an _italic_ word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"
        result = text_to_textnodes(text)
        self.assertEqual(result, [
            TextNode("This is ", TextType.TEXT),
            TextNode("text", TextType.BOLD),
            TextNode(" with an ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" word and a ", TextType.TEXT),
            TextNode("code block", TextType.CODE),
            TextNode(" and an ", TextType.TEXT),
            TextNode("obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
            TextNode(" and a ", TextType.TEXT),
            TextNode("link", TextType.LINK, "https://boot.dev"),
        ])

    def test_plain_text(self):
        result = text_to_textnodes("just plain text")
        self.assertEqual(result, [TextNode("just plain text", TextType.TEXT)])

    def test_bold_only(self):
        result = text_to_textnodes("**bold**")
        self.assertEqual(result, [
            TextNode("", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
            TextNode("", TextType.TEXT),
        ])

    def test_italic_only(self):
        result = text_to_textnodes("_italic_")
        self.assertEqual(result, [
            TextNode("", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode("", TextType.TEXT),
        ])

    def test_code_only(self):
        result = text_to_textnodes("`code`")
        self.assertEqual(result, [
            TextNode("", TextType.TEXT),
            TextNode("code", TextType.CODE),
            TextNode("", TextType.TEXT),
        ])

    def test_image_only(self):
        result = text_to_textnodes("![cat](https://example.com/cat.png)")
        self.assertEqual(result, [
            TextNode("cat", TextType.IMAGE, "https://example.com/cat.png"),
        ])

    def test_link_only(self):
        result = text_to_textnodes("[google](https://google.com)")
        self.assertEqual(result, [
            TextNode("google", TextType.LINK, "https://google.com"),
        ])

    def test_image_and_link(self):
        result = text_to_textnodes("![img](https://example.com/img.png) and [link](https://example.com)")
        self.assertEqual(result, [
            TextNode("img", TextType.IMAGE, "https://example.com/img.png"),
            TextNode(" and ", TextType.TEXT),
            TextNode("link", TextType.LINK, "https://example.com"),
        ])

    def test_bold_and_italic(self):
        result = text_to_textnodes("**bold** and _italic_")
        self.assertEqual(result, [
            TextNode("", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
            TextNode(" and ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode("", TextType.TEXT),
        ])

    def test_multiple_same_type(self):
        result = text_to_textnodes("**a** and **b**")
        self.assertEqual(result, [
            TextNode("", TextType.TEXT),
            TextNode("a", TextType.BOLD),
            TextNode(" and ", TextType.TEXT),
            TextNode("b", TextType.BOLD),
            TextNode("", TextType.TEXT),
        ])


if __name__ == "__main__":
    unittest.main()