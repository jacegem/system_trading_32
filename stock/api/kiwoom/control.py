import time

from PyQt5.QAxContainer import QAxWidget


class Control(QAxWidget):
    def __init__(self):
        super().__init__()
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")

        while self.dynamicCall("GetConnectState()") == 0:
            ret = self.dynamicCall("CommConnect()")
            time.sleep(5)

        if self.dynamicCall("GetConnectState()") == 0:
            print("Not connected")
        else:
            print("Connected")

    def login(self):
        pass
