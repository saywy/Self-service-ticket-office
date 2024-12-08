import sys
from PyQt6.QtWidgets import QApplication
from ui import SelfServiceKiosk

if __name__ == "__main__":
    app = QApplication(sys.argv)
    kiosk = SelfServiceKiosk()
    kiosk.show()
    sys.exit(app.exec())