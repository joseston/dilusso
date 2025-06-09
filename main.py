# app/main.py
import sys
from PyQt5.QtWidgets import QApplication
from time_tracker import TimeTracker

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TimeTracker()
    window.show()
    sys.exit(app.exec_())