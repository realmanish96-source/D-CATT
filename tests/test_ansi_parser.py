import unittest

from app.core.ansi_parser import ANSIParser


class ANSIParserHistoryTests(unittest.TestCase):
    def setUp(self):
        self.parser = ANSIParser(columns=16, rows=3)
        self.parser.feed(
            "line0\r\nline1\r\nline2\r\nline3\r\nline4\r\nline5"
        )

    def test_scrollback_includes_history_and_returns_to_live_screen(self):
        self.parser.scroll_up(100)

        self.assertEqual(
            [line.strip() for line in self.parser.get_display().splitlines()],
            ["line0", "line1", "line2"]
        )

        self.parser.scroll_down(100)

        self.assertEqual(
            [line.strip() for line in self.parser.get_display().splitlines()],
            ["line3", "line4", "line5"]
        )

    def test_new_output_preserves_scrollback_view(self):
        self.parser.scroll_up(2)
        view_before_output = self.parser.get_display()

        self.parser.feed("\r\nline6")

        self.assertEqual(self.parser.get_display(), view_before_output)
        self.assertEqual(self.parser.scroll_offset, 3)
        self.assertEqual(
            self.parser.screen.history.position,
            self.parser.screen.history.size
        )


if __name__ == "__main__":
    unittest.main()
