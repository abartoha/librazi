from PyQt5.QtWidgets import QMainWindow, QTabWidget
from PyQt5.QtGui import QIcon

class MainWindow(QMainWindow):
    def __init__(self, book_view):
        super().__init__()
        self.setWindowTitle("Librazi")
        self.setWindowIcon(QIcon("icon.png"))
        self.setGeometry(100, 100, 1200, 800)
        tabs = QTabWidget()
        tabs.addTab(book_view, "Book Management")
        # Add other views as tabs here
        self.setCentralWidget(tabs)