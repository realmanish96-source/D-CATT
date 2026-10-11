import sys
from PySide6.QtWidgets import QApplication,QPushButton,QLabel,QWidget,QVBoxLayout, QHBoxLayout,QMainWindow,QPlainTextEdit
from PySide6.QtCore import Qt

class MainTerminalWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.textarea()
    #basic terminal winodw UI
    def initUI(self):


        self.setWindowTitle("D-CATT")
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.vertical_layout = QVBoxLayout(central_widget)

        #self.default_font = QLabel("Hello and Welcome to the D-CATT")
        #self.vertical_layout.addWidget(self.default_font)

        #self.default_font.setAlignment(Qt.AlignTop)

        self.setStyleSheet("""
                            QMainWindow{
                            background-color:black;
                                        }
                            QPlainTextEdit{
                            background-color:black;
                            border: none;
                            font-size: 17px;
                            color: white;
                                        }
                            """)

    #text area
    def textarea(self):
        self.termainlediting = QPlainTextEdit()
        self.vertical_layout.addWidget(self.termainlediting)

        


def Front_Window():
    terminal = QApplication(sys.argv)
    window = MainTerminalWindow()
    window.showMaximized()
    sys.exit(terminal.exec())


if (__name__ == '__main__'):
    Front_Window()