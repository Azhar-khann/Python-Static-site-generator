import unittest

from main import extract_title


class TestExtractTitle(unittest.TestCase):

    def test_simple_title(self):
        self.assertEqual(extract_title("# Hello"), "Hello")

    def test_title_with_multiple_words(self):
        self.assertEqual(extract_title("# Hello World"), "Hello World")

    def test_title_with_leading_trailing_whitespace(self):
        # markdown_to_blocks strips the block, so whitespace around # heading is handled
        self.assertEqual(extract_title("  # Hello  "), "Hello")

    def test_title_followed_by_content(self):
        md = "# My Title\n\nSome paragraph text here."
        self.assertEqual(extract_title(md), "My Title")

    def test_title_with_hash_in_text(self):
        # A '#' inside the title text should be preserved
        self.assertEqual(extract_title("# Title with #hashtag"), "Title with #hashtag")

    def test_no_title_raises(self):
        with self.assertRaises(Exception):
            extract_title("Just a plain paragraph")

    def test_h2_raises(self):
        # h2 is not h1 — should raise
        with self.assertRaises(Exception):
            extract_title("## Not a title")

    def test_h1_not_first_block_raises(self):
        # current implementation only finds h1 if it's the first block
        with self.assertRaises(Exception):
            extract_title("Some paragraph\n\n# Title later")

    def test_missing_space_after_hash_raises(self):
        # '#Hello' is not a valid h1 (no space after #)
        with self.assertRaises(Exception):
            extract_title("#NoSpace")

    def test_title_with_trailing_hash(self):
        # trailing '#' in title text must be preserved (e.g. language names like C#)
        self.assertEqual(extract_title("# C#"), "C#")


if __name__ == "__main__":
    unittest.main()
