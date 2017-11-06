import sys

from PyQt5.QtWidgets import QApplication

from .control import Control


class Kiwoom:
    def __init__(self):
        self.account_cnt = ""
        self.account_no_list = []
        self.account_no = ""
        self.user_id = ""
        self.user_name = ""

        self.app = QApplication(sys.argv)
        self.control = Control()

    def get_login_info(self):
        self.account_cnt = self.control.get_login_info('ACCOUNT_CNT')
        self.account_no_list = self.control.get_login_info("ACCNO").split(';')
        self.account_no = self.account_no_list[0]
        self.user_id = self.control.get_login_info("USER_ID")
        self.user_name = self.control.get_login_info("USER_NAME")
        info = "ACCOUNT_CNT:{}\nACCNO:{}\nUSER_ID:{}\nUSER_NAME:{}".format(self.account_cnt, self.account_no,
                                                                           self.user_id, self.user_name)
        print(info)
        return info

    def do(self):
        info = self.get_login_info()
        self.inquiry_balance()
        # self.control.set_input_value("종목코드", "185490")
        # self.control.comm_rq_data("주식기본정보", "OPT10001", 0, "0101")0
        print("END DO")

    def inquiry_balance(self):
        # 예수금상세현황요청
        self.control.set_input_value("계좌번호", self.account_no)
        self.control.set_input_value("비밀번호", "0000")
        self.control.comm_rq_data("예수금상세현황요청", "opw00001", 0, "2000")

        # 계좌평가잔고내역요청 - opw00018 은 한번에 20개의 종목정보를 반환
        self.control.set_input_value("계좌번호", self.account_no)
        self.control.set_input_value("비밀번호", "0000")
        self.control.comm_rq_data("계좌평가잔고내역요청", "opw00018", 0, "2000")
