import sys, time
from PyQt5.QtWidgets import QApplication
from .control import Control


class Kiwoom:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.control = Control()
        pass

    def login(self):
        pass
