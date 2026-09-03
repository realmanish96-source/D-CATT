import sys
from PySide6.QtWidgets import QApplication,QPushButton,QLabel,QWidget,QVBoxLayout, QHBoxLayout,QMainWindow,QSplashScreen
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap,QIcon

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

    #logo
    terminal.setWindowIcon(QIcon("D-CATT\\app\\assets\\D-CATT logo.png"))
    #splash screen
    pixmap = QPixmap("D-CATT\\app\\assets\\D-CATT logo.png")
    pixmap = pixmap.scaled(
        200,
        200,
        Qt.KeepAspectRatio,
        Qt.SmoothTransformation
    )
    splash = QSplashScreen(pixmap)
    splash.show()

    window = MainTerminalWindow()
    window.showMaximized()
    splash.finish(window)
    sys.exit(terminal.exec())


if (__name__ == '__main__'):
    Front_Window()