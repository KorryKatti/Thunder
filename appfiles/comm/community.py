import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView

class WebWindow(QMainWindow):
    def __init__(self, url):
        super().__init__()
        
        self.setWindowTitle("Embedded Web Page")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.browser = QWebEngineView()
        self.layout.addWidget(self.browser)
        self.browser.load(QUrl(url))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    url = "https://www.example.com"
    window = WebWindow(url)
    window.show()
    sys.exit(app.exec_())
