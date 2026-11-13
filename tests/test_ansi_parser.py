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

    def test_alternate_screen_restores_main_content_and_cursor(self):
        parser = ANSIParser(columns=16, rows=3)
        parser.feed("shell prompt")
        parser.feed("\x1b[?25l")
        main_display = parser.get_display()
        main_cursor = (parser.screen.cursor.x, parser.screen.cursor.y)

        parser.feed("\x1b[?104")
        parser.feed("9h")
        self.assertTrue(parser.screen.alternate_screen_active)
        self.assertNotIn("shell prompt", parser.get_display())
        parser.feed("full-screen app\r\nredraw")

        parser.resize(columns=20, rows=4)
        parser.feed("\x1b[?1049l")

        self.assertFalse(parser.screen.alternate_screen_active)
        self.assertEqual(parser.get_display().splitlines()[0][:12], "shell prompt")
        self.assertEqual(
            (parser.screen.cursor.x, parser.screen.cursor.y),
            main_cursor
        )
        self.assertTrue(parser.screen.cursor.hidden)
        self.assertEqual(len(parser.get_display().splitlines()), 4)
        self.assertEqual(main_display.splitlines()[0][:12], "shell prompt")

    def test_alternate_screen_output_does_not_enter_shell_history(self):
        parser = ANSIParser(columns=8, rows=2)
        parser.feed("shell\r\nprompt")
        history_before = len(parser.screen.history.top)

        parser.feed("\x1b[?1049h")
        parser.feed("application\r\nredraw\r\nmore")
        parser.feed("\x1b[?1049l")

        self.assertEqual(len(parser.screen.history.top), history_before)
        self.assertIn("shell", parser.get_display())
        self.assertIn("prompt", parser.get_display())

    def test_mouse_wheel_sequences_use_active_encoding(self):
        parser = ANSIParser(columns=16, rows=3)
        parser.feed("\x1b[?1000h")
        self.assertTrue(parser.mouse_tracking_enabled)
        self.assertEqual(
            parser.mouse_wheel_sequence(1, 3, 2),
            bytes((0x1B, ord("["), ord("M"), 96, 35, 34))
        )

        parser.feed("\x1b[?1006h")
        self.assertEqual(
            parser.mouse_wheel_sequence(-1, 3, 2),
            b"\x1b[<65;3;2M"
        )

    def test_dec_1048_cursor_save_does_not_consume_decs_savepoint(self):
        parser = ANSIParser(columns=16, rows=3)
        parser.feed("shell")

        parser.feed("\x1b[?1048h\x1b[1;1H\x1b7\x1b[2;3H")
        parser.feed("\x1b[?1048l")
        self.assertEqual(
            (parser.screen.cursor.x, parser.screen.cursor.y),
            (5, 0)
        )

        parser.feed("\x1b8")
        self.assertEqual(
            (parser.screen.cursor.x, parser.screen.cursor.y),
            (0, 0)
        )


if __name__ == "__main__":
    unittest.main()
