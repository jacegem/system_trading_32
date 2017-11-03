import time

from PyQt5.QAxContainer import QAxWidget
from PyQt5.QtCore import QEventLoop


class Control(QAxWidget):
    def __init__(self):
        super().__init__()
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")

        self.loginLoop = None

        # while self.dynamicCall("GetConnectState()") == 0:
        #     self.comm_connect()
        #     time.sleep(2)
        self.comm_connect()

        if self.dynamicCall("GetConnectState()") == 0:
            print("Not connected")
        else:
            print("Connected")

    def commConnect(self):
        ret = self.dynamicCall("CommConnect()")
        self.loginLoop = QEventLoop()
        self.loginLoop.exec_()

    def getLoginInfo(self, tag):
        """
        사용자의 tag에 해당하는 정보를 반환한다.
        tag에 올 수 있는 값은 아래와 같다.

        ACCOUNT_CNT: 전체 계좌의 개수를 반환한다.
        ACCNO: 전체 계좌 목록을 반환한다. 계좌별 구분은 ;(세미콜론) 이다.
        USER_ID: 사용자 ID를 반환한다.
        USER_NAME: 사용자명을 반환한다.
        GetServerGubun: 접속서버 구분을 반환합니다.("1": 모의투자, 그외(빈 문자열포함): 실서버)
        :param tag: string
        :return: string
        """
        cmd = 'GetLoginInfo("{}")'.format(tag)
        info = self.dynamicCall(cmd)
        return info
