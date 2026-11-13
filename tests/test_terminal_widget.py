import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QPoint, QPointF, Qt
from PySide6.QtGui import QColor, QFontMetricsF, QTextCursor
from PySide6.QtWidgets import QApplication

from app.core.ansi_parser import ANSIParser
from app.gui.main_window import TerminalWidget


class _Session:
    def write(self, data):
        pass


class _WheelEvent:
    def __init__(self, delta, x=1, y=1):
        self._delta = delta
        self._position = QPointF(x, y)
        self.accepted = False

    def angleDelta(self):
        return QPoint(0, self._delta)

    def position(self):
        return self._position

    def accept(self):
        self.accepted = True


class _KeyEvent:
    def __init__(self, key):
        self._key = key
        self.accepted = False

    def key(self):
        return self._key

    def text(self):
        return ""

    def modifiers(self):
        return Qt.KeyboardModifier.NoModifier

    def accept(self):
        self.accepted = True


class TerminalWidgetLayoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_last_terminal_row_fits_in_viewport(self):
        parser = ANSIParser(columns=80, rows=24)
        widget = TerminalWidget(
            _Session(),
            parser,
            lambda: None,
            lambda columns, rows: parser.resize(columns, rows)
        )
        widget.resize(700, 600)
        widget.show()
        self.app.processEvents()

        parser.feed(
            "".join(f"{line:04d} history entry\r\n" for line in range(250))
            + "narcissist-os$ "
        )
        widget.setPlainText(parser.get_display())

        last_block = widget.document().findBlockByNumber(
            parser.screen.lines - 1
        )
        last_row_rect = widget.cursorRect(QTextCursor(last_block))

        self.assertIn("narcissist-os$", parser.get_display().splitlines()[-1])
        self.assertLessEqual(
            last_row_rect.y() + last_row_rect.height(),
            widget.viewport().height()
        )
        widget.close()

    def test_terminal_grid_uses_fractional_qt_cell_width(self):
        parser = ANSIParser(columns=80, rows=24)
        resized_to = []
        widget = TerminalWidget(
            _Session(),
            parser,
            lambda: None,
            lambda columns, rows: resized_to.append((columns, rows))
        )
        widget.setStyleSheet(
            "QPlainTextEdit { font-size: 17px; color: white; }"
        )
        widget.resize(700, 600)
        widget.show()
        self.app.processEvents()

        cell_width = QFontMetricsF(widget.font()).horizontalAdvance("M")
        columns = resized_to[-1][0]

        self.assertEqual(columns, int(widget.viewport().width() // cell_width))
        self.assertLessEqual(columns * cell_width, widget.viewport().width())
        widget.close()

    def test_terminal_cursor_uses_qt_layout_position(self):
        parser = ANSIParser(columns=80, rows=24)
        widget = TerminalWidget(
            _Session(),
            parser,
            lambda: None,
            lambda columns, rows: None
        )
        styled_lines = parser.get_styled_display()
        styled_lines[0][55]["bold"] = True
        widget.set_styled_lines(styled_lines)
        widget.set_terminal_cursor(55, 0)
        widget.resize(1200, 700)
        widget.show()
        self.app.processEvents()

        block = widget.document().findBlockByNumber(0)
        expected_cursor = QTextCursor(block)
        expected_cursor.setPosition(block.position() + 55)
        qt_cursor_rect = widget.cursorRect(expected_cursor)
        terminal_cursor_rect = widget._terminal_cursor_rect()

        self.assertEqual(terminal_cursor_rect.x(), qt_cursor_rect.x())
        self.assertEqual(terminal_cursor_rect.y(), qt_cursor_rect.y())
        self.assertEqual(terminal_cursor_rect.height(), qt_cursor_rect.height())
        widget.close()

    def test_styled_refresh_preserves_selection_and_colors(self):
        parser = ANSIParser(columns=8, rows=2)
        widget = TerminalWidget(
            _Session(),
            parser,
            lambda: None,
            lambda columns, rows: None
        )
        widget.set_styled_lines(parser.get_styled_display())
        cursor = QTextCursor(widget.document())
        cursor.setPosition(6)
        cursor.setPosition(1, QTextCursor.MoveMode.KeepAnchor)
        widget.setTextCursor(cursor)

        updated_lines = [
            [cell.copy() for cell in line]
            for line in parser.get_styled_display()
        ]
        updated_lines[0][0]["fg"] = "red"
        widget.set_styled_lines(updated_lines)

        restored_cursor = widget.textCursor()
        self.assertEqual(restored_cursor.anchor(), 6)
        self.assertEqual(restored_cursor.position(), 1)
        color_cursor = QTextCursor(widget.document())
        color_cursor.setPosition(0)
        self.assertEqual(
            color_cursor.charFormat().foreground().color(),
            QColor("red")
        )
        widget.close()

    def test_indexed_truecolor_and_bright_ansi_colors_render(self):
        parser = ANSIParser(columns=8, rows=2)
        parser.feed(
            "\x1b[38;5;196mP"
            "\x1b[38;2;127;0;0mT"
            "\x1b[91mB"
        )
        widget = TerminalWidget(
            _Session(),
            parser,
            lambda: None,
            lambda columns, rows: None
        )
        widget.set_styled_lines(parser.get_styled_display())

        for position, expected_color in enumerate(
            ("#ff0000", "#7f0000", "#ff0000")
        ):
            cursor = QTextCursor(widget.document())
            cursor.setPosition(position + 1)
            self.assertEqual(
                cursor.charFormat().foreground().color(),
                QColor(expected_color)
            )

        widget.close()

    def test_mouse_wheel_is_forwarded_when_application_requests_mouse(self):
        parser = ANSIParser(columns=8, rows=2)
        parser.feed("\x1b[?1000;1006h")
        session = _Session()
        writes = []
        session.write = writes.append
        widget = TerminalWidget(
            session,
            parser,
            lambda: None,
            lambda columns, rows: None
        )
        event = _WheelEvent(120)

        widget.wheelEvent(event)

        self.assertEqual(writes, [b"\x1b[<64;1;1M"])
        self.assertEqual(parser.scroll_offset, 0)
        self.assertTrue(event.accepted)
        widget.close()

    def test_alternate_screen_wheel_does_not_change_shell_scrollback(self):
        parser = ANSIParser(columns=8, rows=2)
        parser.feed("one\r\ntwo\r\nthree")
        parser.feed("\x1b[?1049h")
        session = _Session()
        widget = TerminalWidget(
            session,
            parser,
            lambda: None,
            lambda columns, rows: None
        )
        event = _WheelEvent(120)

        widget.wheelEvent(event)

        self.assertEqual(parser.scroll_offset, 0)
        self.assertTrue(event.accepted)
        widget.close()

    def test_down_arrow_follows_application_cursor_mode(self):
        parser = ANSIParser(columns=8, rows=2)
        session = _Session()
        writes = []
        session.write = writes.append
        widget = TerminalWidget(
            session,
            parser,
            lambda: None,
            lambda columns, rows: None
        )

        normal_event = _KeyEvent(Qt.Key.Key_Down)
        widget.keyPressEvent(normal_event)
        self.assertEqual(writes[-1], b"\x1b[B")

        parser.feed("\x1b[?1h")
        application_event = _KeyEvent(Qt.Key.Key_Down)
        widget.keyPressEvent(application_event)
        self.assertEqual(writes[-1], b"\x1bOB")
        self.assertTrue(application_event.accepted)

        parser.feed("\x1b[?1l")
        widget.keyPressEvent(_KeyEvent(Qt.Key.Key_Down))
        self.assertEqual(writes[-1], b"\x1b[B")
        widget.close()


if __name__ == "__main__":
    unittest.main()
