import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication

from app.core.ansi_parser import ANSIParser
from app.gui.main_window import TerminalWidget


class _Session:
    def write(self, data):
        pass


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


if __name__ == "__main__":
    unittest.main()
