import sys, time
from pandas import DataFrame

from PyQt5.QtWidgets import QApplication

from .control import Control


class SingletonInstane:
    __instance = None

    @classmethod
    def __getInstance(cls):
        return cls.__instance

    @classmethod
    def instance(cls, *args, **kargs):
        cls.__instance = cls(*args, **kargs)
        cls.instance = cls.__getInstance
        return cls.__instance


class Kiwoom(SingletonInstane):

    def __init__(self):
        self.app = QApplication(sys.argv)
        self.control = Control()

        self.account_cnt = ""
        self.account_no_list = []
        self.account_no = ""
        self.user_id = ""
        self.user_name = ""

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
        # self.control.comm_rq_data("주식기본정보", "OPT10001", 0, "0101")
        print("END DO")
        # if Kiwoom.app:
        #     QApplication.quit()
        #     Kiwoom.app = None

    def inquiry_balance(self):
        # 예수금상세현황요청
        self.control.set_input_value("계좌번호", self.account_no)
        self.control.set_input_value("비밀번호", "0000")
        self.control.comm_rq_data("예수금상세현황요청", "opw00001", 0, "2000")

        # 예수금상세현황요청
        self.control.set_input_value("계좌번호", self.account_no)
        self.control.set_input_value("비밀번호", "0000")
        self.control.comm_rq_data("예수금상세현황요청", "opw00001", 0, "2000")

        # 계좌평가잔고내역요청 - opw00018 은 한번에 20개의 종목정보를 반환
        self.control.set_input_value("계좌번호", self.account_no)
        self.control.set_input_value("비밀번호", "0000")
        self.control.comm_rq_data("계좌평가잔고내역요청", "opw00018", 0, "2000")

    def get_run(self):
        df = self.get_ohlcv("039490", "20170321")
        print(df)

    def get_ohlcv(self, code, start):
        self.control.ohlcv = {'date': [], 'open': [], 'high': [], 'low': [], 'close': [], 'volume': []}

        self.control.set_input_value("종목코드", code)
        self.control.set_input_value("기준일자", start)
        self.control.set_input_value("수정주가구분", 1)
        self.control.comm_rq_data("opt10081_req", "opt10081", 0, "0101")
        time.sleep(2.2)

        df = DataFrame(self.control.ohlcv, columns=['open', 'high', 'low', 'close', 'volume'],
                       index=self.control.ohlcv['date'])
        return df