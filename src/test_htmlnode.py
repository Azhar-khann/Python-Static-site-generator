import unittest

from htmlnode import HTMLNODE, LeafNode, ParentNode

class TestHTMLNODE(unittest.TestCase):
    def test_init(self):
        node = HTMLNODE("div", "Hello World", None, {"class": "container"})
        self.assertEqual(node.tag, "div")
        self.assertEqual(node.value, "Hello World")
        self.assertEqual(node.children, None)
        self.assertEqual(node.props, {"class": "container"})

    def test_repr(self):
        node = HTMLNODE("div", "Hello World", None, {"class": "container"})
        expected_repr = "HTMLNODE(tag=div, value=Hello World, children=None, props={'class': 'container'})"
        self.assertEqual(repr(node), expected_repr)

    def test_props_to_html(self):
        node = HTMLNODE("div", "Hello World", None, {"class": "container", "id": "main"})
        expected_props_html = ' class="container" id="main"'
        self.assertEqual(node.props_to_html(), expected_props_html)

class TestLeafNode(unittest.TestCase):

    def test_leaf_to_html_p(self):
        node = LeafNode("p", "Hello, world!")
        self.assertEqual(node.to_html(), "<p>Hello, world!</p>")

    def test_to_html(self):
        node = LeafNode("p", "Hello World", {"class": "text"})
        expected_html = '<p class="text">Hello World</p>'
        self.assertEqual(node.to_html(), expected_html)

    def test_to_html_no_tag(self):
        node = LeafNode(None, "Just text")
        expected_html = 'Just text'
        self.assertEqual(node.to_html(), expected_html)

    def test_to_html_no_value(self):
        node = LeafNode("p", None)
        with self.assertRaises(ValueError):
            node.to_html()

class TestParentNode(unittest.TestCase):

    def test_to_html_with_children(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(parent_node.to_html(), "<div><span>child</span></div>")

    def test_to_html_with_grandchildren(self):
        grandchild_node = LeafNode("b", "grandchild")
        child_node = ParentNode("span", [grandchild_node])
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(
            parent_node.to_html(),
            "<div><span><b>grandchild</b></span></div>",
        )

    def test_to_html_with_two_sibling_parents(self):
        child1 = ParentNode("div", [LeafNode("p", "first")])
        child2 = ParentNode("div", [LeafNode("p", "second")])
        parent_node = ParentNode("section", [child1, child2])
        self.assertEqual(
            parent_node.to_html(),
            "<section><div><p>first</p></div><div><p>second</p></div></section>",
        )

    def test_to_html_parent_with_nested_parent_and_leaf(self):
        nested_parent = ParentNode("span", [LeafNode("b", "bold")])
        leaf = LeafNode("i", "italic")
        child = ParentNode("div", [nested_parent, leaf])
        parent_node = ParentNode("section", [child])
        self.assertEqual(
            parent_node.to_html(),
            "<section><div><span><b>bold</b></span><i>italic</i></div></section>",
        )

