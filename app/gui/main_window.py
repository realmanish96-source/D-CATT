import sys
from pathlib import Path

if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.core.ansi_parser import ANSIParser
from PySide6.QtWidgets import QApplication,QWidget,QVBoxLayout,QMainWindow,QPlainTextEdit
from PySide6.QtCore import QTimer,Qt,QRect
from app.core.session import TerminalSession
from PySide6.QtGui import QPainter,QTextCursor,QFontDatabase

class TerminalWidget(QPlainTextEdit):
    def __init__(self, session,ansi_parser,refresh_callback, resize_callback, parent=None):
        super().__init__(parent)
        self.session = session
        self.ansi_parser = ansi_parser
        self.refresh_callback = refresh_callback
        self.resize_callback = resize_callback
        self.last_terminal_size = None
        self.terminal_cursor = (0, 0)
        self._wheel_remainder = 0

        font = QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont)
        font.setPointSize(17)
        self.setFont(font)
        self.document().setDocumentMargin(0)
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setFocus()
        self.setCursorWidth(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)

        cell_width = self.fontMetrics().horizontalAdvance("M")
        cell_height = self.cursorRect().height()
        if cell_height <= 0:
            cell_height = self.fontMetrics().lineSpacing()
        if cell_width <= 0 or cell_height <= 0:
            return

        columns = self.viewport().width() // cell_width
        rows = self.viewport().height() // cell_height
        if columns <= 0 or rows <= 0:
            return

        size = (columns, rows)
        if size != self.last_terminal_size:
            self.last_terminal_size = size
            self.resize_callback(columns, rows)

    #single click control
    def mousePressEvent(self, event):
        super().mousePressEvent(event)


    def mouseDoubleClickEvent(self, event):
        super().mouseDoubleClickEvent(event)

    def set_terminal_cursor(self, x, y):
        self.terminal_cursor = (x, y)
        self.viewport().update()

    def paintEvent(self, event):
        super().paintEvent(event)

        x, y = self.terminal_cursor
        y = self.ansi_parser.get_cursor_display_row(y)
        cell_width = self.fontMetrics().horizontalAdvance("M")
        cell_height = self.fontMetrics().lineSpacing()
        if y is None or cell_width <= 0 or cell_height <= 0:
            return

        line = self.document().findBlockByNumber(y)
        if not line.isValid():
            return

        line_rect = self.cursorRect(QTextCursor(line))
        x = min(max(x, 0), self.ansi_parser.screen.columns - 1)
        cursor_rect = QRect(
            x * cell_width,
            line_rect.top(),
            2,
            max(cell_height, line_rect.height())
        )
        if not self.viewport().rect().intersects(cursor_rect):
            return

        painter = QPainter(self.viewport())
        painter.fillRect(cursor_rect, Qt.GlobalColor.white)

    #right click control
    def contextMenuEvent(self, event):
        event.accept()

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        if delta:
            self._wheel_remainder += delta
            steps = int(self._wheel_remainder / 120)
            self._wheel_remainder -= steps * 120
            lines = abs(steps) * 3
            if steps > 0:
                self.ansi_parser.scroll_up(lines)
            elif steps < 0:
                self.ansi_parser.scroll_down(lines)
            if steps:
                self.refresh_callback()

        event.accept()

    def keyPressEvent(self, event):
        key = event.key()
        text = event.text()
        modifiers = event.modifiers()

        #arrow keys
        arrow_keys = {
            Qt.Key.Key_Up: b"\x1b[A",
            Qt.Key.Key_Down: b"\x1b[B",
            Qt.Key.Key_Right: b"\x1b[C",
            Qt.Key.Key_Left: b"\x1b[D"
        }
        if key in arrow_keys:
            self.session.write(arrow_keys[key])
            event.accept()
            return

        #special keys 
        special_keys = {
            Qt.Key.Key_Up: b"\x1b[A",
            Qt.Key.Key_Down: b"\x1b[B",
            Qt.Key.Key_Right: b"\x1b[C",
            Qt.Key.Key_Left: b"\x1b[D",
            Qt.Key.Key_Return: b"\r",
            Qt.Key.Key_Enter: b"\r",
            Qt.Key.Key_Backspace: b"\x7f",
            Qt.Key.Key_Tab: b"\t",
            Qt.Key.Key_Escape: b"\x1b"
        }
        if key in special_keys:
            self.session.write(special_keys[key])
            event.accept()
            return

        # Ctrl+Shift+C copy method
        if (
            modifiers
            == Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.ShiftModifier and key == Qt.Key.Key_C
        ):
            self.copy()
            event.accept()
            return

        #Ctrl+Shift+V paste method
        if(
            modifiers == Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.ShiftModifier and key == Qt.Key.Key_V
        ):
            clipboard = QApplication.clipboard()
            text = clipboard.text()

            if text:
                self.session.write(text.encode("utf-8"))

            event.accept()
            return

        #Ctrl+C function
        if(modifiers == Qt.KeyboardModifier.ControlModifier and key == Qt.Key.Key_C):
            self.session.write(b"\x03")
            event.accept()
            return

        # Enter
        if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.session.write(b"\n")
            event.accept()
            return

        # Backspace
        if key == Qt.Key.Key_Backspace:
            self.session.write(b"\x7f")
            event.accept()
            return

        if text:
            self.session.write(
                text.encode("utf-8")
            )
            event.accept()
            return

        event.ignore()

    
class MainTerminalWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Terminal backend
        self.session = TerminalSession()
        self.session.start()

        self.ansi_parser = ANSIParser(columns=80, rows=24)

        self.initUI()
        self.textarea()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.read_terminal_output)
        self.timer.start(50)

    def update_terminal_cursor(self, x, y):
        self.termainlediting.set_terminal_cursor(x, y)

    def initUI(self):
        self.setWindowTitle("D-CATT")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.vertical_layout = QVBoxLayout(central_widget)

        self.setStyleSheet("""
            QMainWindow {
                background-color: black;
            }

            QPlainTextEdit {
                background-color: black;
                border: none;
                font-size: 17px;
                color: white;
            }
        """)

    def textarea(self):
        self.termainlediting = TerminalWidget(
        self.session,
        self.ansi_parser,
        self.render_terminal,
        self.resize_terminal,
        self
    )

        self.vertical_layout.addWidget(
        self.termainlediting
    )

        self.termainlediting.setFocus()

    def render_terminal(self):
        display = self.ansi_parser.get_display()

        if self.termainlediting.toPlainText() != display:
            cursor = self.termainlediting.textCursor()
            anchor = cursor.anchor()
            position = cursor.position()

            self.termainlediting.setPlainText(display)

            last_position = self.termainlediting.document().characterCount() - 1
            cursor = QTextCursor(self.termainlediting.document())
            cursor.setPosition(min(anchor, last_position))
            cursor.setPosition(
                min(position, last_position),
                QTextCursor.MoveMode.KeepAnchor
            )
            self.termainlediting.setTextCursor(cursor)

        self.update_terminal_cursor(
            self.ansi_parser.screen.cursor.x,
            self.ansi_parser.screen.cursor.y
        )

    def resize_terminal(self, columns, rows):
        self.ansi_parser.resize(columns, rows)
        self.session.resize(rows, columns)

    def keyPressEvent(self, event):
        text = event.text()

        if text:
            self.session.write(text.encode())

        elif event.key()== Qt.Key.Key_Return:
            self.session.write(b"\n")

        elif event.key() == Qt.Key.Key_Backspace:
            self.session.write(b"\x7f")

        event.accept()

    def read_terminal_output(self):
        data = self.session.read(timeout=0)

        if data is None:
            return

        if data == b"":
            self.timer.stop()
            return

    # Feed PTY output into ANSI parser
        self.ansi_parser.feed(data)

    # Render the current terminal screen
        self.render_terminal()

    def closeEvent(self, event):
        self.timer.stop()
        self.session.close()

        event.accept()


if __name__ == "__main__":
    from runpy import run_path

    run_path(
        str(Path(__file__).resolve().parents[2] / "main.py"),
        run_name="__main__",
    )