import logging
import logging.config

from PyQt5.QAxContainer import QAxWidget
from PyQt5.QtCore import QEventLoop

from .code import *
from .error import *


class Control(QAxWidget):
    def __init__(self):
        super().__init__()
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")

        self.event_loop = None
        self.request_loop = None
        self.order_loop = None
        self.condition_loop = None

        self.order_no = ""  # 주문번호
        self.inquiry = 0  # 조회
        self.msg = ""
        self.condition = ""

        self.opw00001Data = {}
        self.opw00018Data = {}

        self.OnEventConnect.connect(self.event_connect)
        self.OnReceiveMsg.connect(self.receive_msg)
        self.OnReceiveTrData.connect(self.receive_tr_data)
        self.OnReceiveConditionVer.connect(self.receive_condition_ver)

        # 로깅용 설정파일
        logging.config.fileConfig('logging.conf')
        self.log = logging.getLogger('Kiwoom')

        if self.get_connect_state() == 0:
            self.comm_connect()

    def receive_condition_ver(self, receive, msg):
        """
        getConditionLoad() 메서드의 조건식 목록 요청에 대한 응답 이벤트
        :param receive: int - 응답결과(1: 성공, 나머지 실패)
        :param msg: string - 메세지
        """
        self.log.info("<<receiveConditionVer>>")
        self.log.debug("receive, msg : ({}, {})".format(receive, msg))

        try:
            if not receive:
                return

            self.condition = self.getConditionNameList()
            print("조건식 개수: ", len(self.condition))

            for key in self.condition.keys():
                print("조건식: ", key, ": ", self.condition[key])
                print("key type: ", type(key))

        except Exception as e:
            print(e)

        finally:
            self.condition_loop.exit()

    def receive_msg(self, screen_no, request_name, tr_code, msg):
        """
        수신 메시지 이벤트
        서버로 어떤 요청을 했을 때(로그인, 주문, 조회 등), 그 요청에 대한 처리내용을 전달해준다.
        :param screen_no: string - 화면번호(4자리, 사용자 정의, 서버에 조회나 주문을 요청할 때 이 요청을 구별하기 위한 키값)
        :param request_name: string - TR 요청명(사용자 정의)
        :param tr_code: string
        :param msg: string - 서버로 부터의 메시지
        """
        self.log.info("<<receiveMsg>>")
        self.log.debug("screenNo, request_name, tr_code, msg : {}, {}, {}, {}".format(screen_no, request_name, tr_code, msg))
        self.msg += request_name + ": " + msg + "\r\n\r\n"

    def comm_connect(self):
        self.dynamicCall("CommConnect()")
        self.event_loop = QEventLoop()
        self.event_loop.exec_()
        print('after comm_connect')

    def event_connect(self, code):
        print("event_connect", code)
        try:
            if code == ReturnCode.OP_ERR_NONE:
                print('연결성공')
            else:
                print('연결실패')
        finally:
            self.event_loop.exit()

    def get_login_info(self, tag):
        """
        사용자의 tag에 해당하는 정보를 반환한다.
        tag에 올 수 있는 값은 아래와 같다.

        ACCOUNT_CNT: 전체 계좌의 개수를 반환한다.
        ACCNO: 전체 계좌 목록을 반환한다. 계좌별 구분은 ;(세미콜론) 이다.
        USER_ID: 사용자 ID를 반환한다.
        USER_NAME: 사용자명을 반환한다.

        :param tag: string
        :return: string
        """
        cmd = 'GetLoginInfo("{}")'.format(tag)
        info = self.dynamicCall(cmd)
        return info

    def set_input_value(self, key, value):
        """
        TR 전송에 필요한 값을 설정한다.
        :param key: string - TR에 명시된 input 이름
        :param value: string - key에 해당하는 값
        """
        self.dynamicCall("SetInputValue(QString, QString)", key, value)

    def get_connect_state(self):
        """
        현재 접속상태를 반환합니다.
        반환되는 접속상태는 아래와 같습니다.
        0: 미연결, 1: 연결
        :return: int
        """
        self.log.info("[getConnectState]")

        state = self.dynamicCall("GetConnectState()")
        return state

    def comm_rq_data(self, request_name, tr_code, inquiry, screen_no):
        """
        키움서버에 TR 요청을 한다.
        조회요청메서드이며 빈번하게 조회요청시, 시세과부하 에러값 -200이 리턴된다.
        :param request_name: string - TR 요청명(사용자 정의)
        :param tr_code: string
        :param inquiry: int - 조회(0: 조회, 2: 남은 데이터 이어서 요청)
        :param screen_no: string - 화면번호(4자리)
        """
        self.log.info("[commRqData]")
        self.log.debug(
            "requestName, trCode, inquiry, screenNo : ({}, {}, {}, {})".format(request_name, tr_code, inquiry,
                                                                               screen_no))

        if not self.get_connect_state():
            raise KiwoomConnectError()

        if not (isinstance(request_name, str)
                and isinstance(tr_code, str)
                and isinstance(inquiry, int)
                and isinstance(screen_no, str)):
            raise ParameterTypeError()

        return_code = self.dynamicCall("CommRqData(QString, QString, int, QString)", request_name, tr_code, inquiry,
                                       screen_no)

        if return_code != ReturnCode.OP_ERR_NONE:
            raise KiwoomProcessingError("commRqData(): " + ReturnCode.CAUSE[return_code])

            # 루프 생성: receiveTrData() 메서드에서 루프를 종료시킨다.
            # self.request_loop = QEventLoop()
            # self.request_loop.exec_()

    def receive_tr_data(self, screen_no, request_name, tr_code, record_name, inquiry,
                        deprecated1, deprecated2, deprecated3, deprecated4):
        """
        TR 수신 이벤트
        조회요청 응답을 받거나 조회데이터를 수신했을 때 호출됩니다.
        requestName과 trCode는 commRqData()메소드의 매개변수와 매핑되는 값 입니다.
        조회데이터는 이 이벤트 메서드 내부에서 getCommData() 메서드를 이용해서 얻을 수 있습니다.
        :param screen_no: string - 화면번호(4자리)
        :param request_name: string - TR 요청명(commRqData() 메소드 호출시 사용된 requestName)
        :param tr_code: string
        :param record_name: string
        :param inquiry: string - 조회('0': 남은 데이터 없음, '2': 남은 데이터 있음)
        :param deprecated1:
        :param deprecated2
        :param deprecated3
        :param deprecated4
        """
        self.log.info("<<receiveTrData>>")
        self.log.debug(
            "screenNo, requestName, trCode, recordName, inquiry, deprecated1, deprecated2, deprecated3, deprecated4 : {0:5} {1:10} {2:5} {3:3}".format(
                screen_no, request_name, tr_code, record_name, inquiry, deprecated1, deprecated2, deprecated3,
                deprecated4))

        if self.request_loop:
            self.request_loop.exit()

        pass

        # 주문번호와 주문루프
        self.order_no = self.get_comm_data(tr_code, request_name, 0, "주문번호")

        if self.order_loop:
            self.order_loop.exit()

        self.inquiry = inquiry

        if request_name == "관심종목정보요청":
            self.data = self.get_comm_data_ex(tr_code, "관심종목정보")
            print(type(self.data))
            print(self.data)

            """ getCommData
            cnt = self.getRepeatCnt(trCode, requestName)
            for i in range(cnt):
                data = self.getCommData(trCode, requestName, i, "종목명")
                print(data)
            """

        elif request_name == "주식틱차트조회요청":
            self.data = self.get_comm_data_ex(tr_code, "주식틱차트조회")

        elif request_name == "주식일봉차트조회요청":
            self.data = self.get_comm_data_ex(tr_code, "주식일봉차트조회")

        elif request_name == "예수금상세현황요청":
            deposit = self.get_comm_data(tr_code, request_name, 0, "d+2추정예수금")
            deposit = self.change_format(deposit)
            self.opw00001Data = deposit

        elif request_name == "계좌평가잔고내역요청":
            # 계좌 평가 정보
            account_evaluation = []
            key_list = ["총매입금액", "총평가금액", "총평가손익금액", "총수익률(%)", "추정예탁자산"]

            for key in key_list:
                value = self.get_comm_data(tr_code, request_name, 0, key)

                # if key.startswith("총수익률"):
                #     value = self.changeFormat(value, 1)
                # else:
                #     value = self.changeFormat(value)

                account_evaluation.append(value)

            self.opw00018Data['accountEvaluation'] = account_evaluation

            # 보유 종목 정보
            cnt = self.get_repeat_cnt(tr_code, request_name)
            key_list = ["종목명", "종목번호", "보유수량", "매입가", "현재가", "평가손익", "수익률(%)"]

            for i in range(cnt):
                stock = []

                for key in key_list:
                    value = self.get_comm_data(tr_code, request_name, i, key)

                    if key.startswith("수익률"):
                        value = self.changeFormat(value, 2)
                    elif key != "종목번호" and key != "종목명":
                        value = self.changeFormat(value)

                    stock.append(value)

                self.opw00018Data['stocks'].append(stock)

        if self.request_loop:
            self.request_loop.exit()

    def get_comm_data(self, tr_code, request_name, index, key):
        """
        데이터 획득 메서드
        receiveTrData() 이벤트 메서드가 호출될 때, 그 안에서 조회데이터를 얻어오는 메서드입니다.
        :param tr_code: string
        :param request_name: string - TR 요청명(commRqData() 메소드 호출시 사용된 requestName)
        :param index: int
        :param key: string - 수신 데이터에서 얻고자 하는 값의 키(출력항목이름)
        :return: string
        """
        self.log.info("[getCommData]")
        self.log.debug("trCode, requestName, index, key : ({}, {}, {}, {})".format(tr_code, request_name, index, key))

        if not (isinstance(tr_code, str)
                and isinstance(request_name, str)
                and isinstance(index, int)
                and isinstance(key, str)):
            raise ParameterTypeError()

        data = self.dynamicCall("GetCommData(QString, QString, int, QString)",
                                tr_code, request_name, index, key)
        return data.strip()

    def get_comm_data_ex(self, tr_code, multi_data_name):
        """
        멀티데이터 획득 메서드
        receiveTrData() 이벤트 메서드가 호출될 때, 그 안에서 사용해야 합니다.
        :param tr_code: string
        :param multi_data_name: string - KOA에 명시된 멀티데이터명
        :return: list - 중첩리스트
        """
        self.log.info("[getCommDataEx]")
        self.log.debug("trCode, multiDataName : ({}, {})".format(tr_code, multi_data_name))

        if not (isinstance(tr_code, str)
                and isinstance(multi_data_name, str)):
            raise ParameterTypeError()

        data = self.dynamicCall("GetCommDataEx(QString, QString)", tr_code, multi_data_name)
        return data

    def change_format(self, data, percent=0):
        self.log.info("[changeFormat]")
        self.log.debug("data, percent : ({})".format(data, percent))

        if percent == 0:
            d = int(data)
            format_data = '{:-,d}'.format(d)

        elif percent == 1:
            f = int(data) / 100
            format_data = '{:-,.2f}'.format(f)

        elif percent == 2:
            f = float(data)
            format_data = '{:-,.2f}'.format(f)

        return format_data

    def get_repeat_cnt(self, tr_code, request_name):
        """
        서버로 부터 전달받은 데이터의 갯수를 리턴합니다.(멀티데이터의 갯수)
        receiveTrData() 이벤트 메서드가 호출될 때, 그 안에서 사용해야 합니다.
        키움 OpenApi+에서는 데이터를 싱글데이터와 멀티데이터로 구분합니다.
        싱글데이터란, 서버로 부터 전달받은 데이터 내에서, 중복되는 키(항목이름)가 하나도 없을 경우.
        예를들면, 데이터가 '종목코드', '종목명', '상장일', '상장주식수' 처럼 키(항목이름)가 중복되지 않는 경우를 말합니다.
        반면 멀티데이터란, 서버로 부터 전달받은 데이터 내에서, 일정 간격으로 키(항목이름)가 반복될 경우를 말합니다.
        예를들면, 10일간의 일봉데이터를 요청할 경우 '종목코드', '일자', '시가', '고가', '저가' 이러한 항목이 10번 반복되는 경우입니다.
        이러한 멀티데이터의 경우 반복 횟수(=데이터의 갯수)만큼, 루프를 돌면서 처리하기 위해 이 메서드를 이용하여 멀티데이터의 갯수를 얻을 수 있습니다.
        :param tr_code: string
        :param request_name: string - TR 요청명(commRqData() 메소드 호출시 사용된 requestName)
        :return: int
        """
        self.log.info("[getRepeatCnt]")
        self.log.debug("tr_code, request_name : ({}, {})".format(tr_code, request_name))

        if not (isinstance(tr_code, str)
                and isinstance(request_name, str)):
            raise ParameterTypeError()

        count = self.dynamicCall("GetRepeatCnt(QString, QString)", tr_code, request_name)
        return count
