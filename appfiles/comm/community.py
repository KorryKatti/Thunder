import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Embedded Web Browser")
        self.setGeometry(100, 100, 800, 600)

        web_view = QWebEngineView()
        web_view.setUrl(QUrl('https://example.com'))  # Create QUrl object from URL string
        self.setCentralWidget(web_view)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
