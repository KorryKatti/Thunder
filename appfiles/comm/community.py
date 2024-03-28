import sys
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWebEngineWidgets import QWebEngineView

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Embedded Web Page")
        self.setGeometry(100, 100, 800, 600)
        
        self.browser = QWebEngineView()
        self.setCentralWidget(self.browser)
        
        # Load URL
        url = QUrl("https://www.wikipedia.org")
        self.browser.setUrl(url)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
