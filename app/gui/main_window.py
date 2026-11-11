import sys
from app.core.ansi_parser import ANSIParser
from PySide6.QtWidgets import QApplication,QWidget,QVBoxLayout,QMainWindow,QPlainTextEdit
from PySide6.QtCore import QTimer,Qt
from app.core.session import TerminalSession
from PySide6.QtGui import QTextCursor,QGuiApplication,QFont

class TerminalWidget(QPlainTextEdit):
    def __init__(self, session, parent=None):
        super().__init__(parent)
        self.session = session

        self.setFocus()

    #single click control
    def mousePressEvent(self, event):
        self.setFocus()
        event.accept()
    #double click control
    def mouseDoubleClickEvent(self, event):
        self.setFocus()
        event.accept()
    #right click control
    def contextMenuEvent(self, event):
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

        self.ansi_parser = ANSIParser(columns= 120, rows=30)

        self.initUI()
        self.textarea()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.read_terminal_output)
        self.timer.start(50)

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
        self
    )

        self.vertical_layout.addWidget(
        self.termainlediting
    )

        self.termainlediting.setFocus()

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

        self.ansi_parser.feed(data)

        display = self.ansi_parser.get_display()
        self.termainlediting.setPlainText(display)

        x = self.ansi_parser.screen.cursor.x
        y = self.ansi_parser.screen.cursor.y

        cursor = self.termainlediting.textCursor()

        cursor.movePosition(QTextCursor.MoveOperation.Start)

        cursor.movePosition(
        QTextCursor.MoveOperation.Down,
        QTextCursor.MoveMode.MoveAnchor,y
        )

        cursor.movePosition(
        QTextCursor.MoveOperation.Right,
        QTextCursor.MoveMode.MoveAnchor,x
        )       

        self.termainlediting.setTextCursor(cursor)

    def closeEvent(self, event):
        self.timer.stop()
        self.session.close()

        event.accept()