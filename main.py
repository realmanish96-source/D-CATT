#system import
import sys

#gui import
from PySide6.QtWidgets import QApplication,QSplashScreen
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import Qt

#internal file imports
from app.gui.main_window import MainTerminalWindow
from app.utils.path import LOGO


def main():

    app = QApplication(sys.argv)
    
    app.setWindowIcon(QIcon(str(LOGO)))

    #splash screen
    pixmap = QPixmap(str(LOGO))
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
    sys.exit(app.exec())


if __name__ == "__main__":
    main()