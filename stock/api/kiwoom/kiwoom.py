import sys

from PyQt5.QtWidgets import QApplication

from .control import Control


class Kiwoom:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.control = Control()
        pass

    def get_login_info(self):
        info = self.control.get_login_info('ACCOUNT_CNT')
        print(info)
        pass

    def do(self):
        self.get_login_info()
