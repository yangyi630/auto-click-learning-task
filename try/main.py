import sys
import os
import site

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(site.getusersitepackages())

from modules.gui import MainWindow
from PyQt5.QtWidgets import QApplication

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()