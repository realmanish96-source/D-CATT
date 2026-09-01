import sys
from PySide6.QtWidgets import QApplication,QPushButton,QLabel,QWidget,QVBoxLayout, QHBoxLayout

class Main_terminal_Window(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.default_font = QLabel("Hello and Welcome to the D-CATT",self)

    def initUI(self):
        self.setWindowTitle("D-CATT")
        


def Front_Window():
    terminal = QApplication(sys.argv)
    window = Main_terminal_Window()
    window.showMaximized()
    sys.exit(terminal.exec())

if (__name__ == '__main__'):
    Front_Window()