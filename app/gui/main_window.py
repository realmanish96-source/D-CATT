import sys
from PySide6.QtWidgets import QApplication,QPushButton,QLabel,QWidget,QVBoxLayout, QHBoxLayout,QMainWindow
from PySide6.QtCore import Qt

class MainTerminalWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):


        self.setWindowTitle("D-CATT")
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        vertical_layout = QVBoxLayout(central_widget)

        self.default_font = QLabel("Hello and Welcome to the D-CATT")
        vertical_layout.addWidget(self.default_font)

        self.default_font.setAlignment(Qt.AlignTop)

        self.setStyleSheet("""
                            QMainWindow{
                            background-color: black;
                                        }
                            """)


        


def Front_Window():
    terminal = QApplication(sys.argv)
    window = MainTerminalWindow()
    window.showMaximized()
    sys.exit(terminal.exec())


if (__name__ == '__main__'):
    Front_Window()