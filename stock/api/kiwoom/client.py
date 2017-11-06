import pythoncom, win32com.client


class Client:
    def __init__(self):
        # https://stackoverflow.com/questions/26764978/using-win32com-with-multithreading
        pythoncom.CoInitialize()
        self.control = win32com.client.Dispatch("KHOPENAPI.KHOpenAPICtrl.1")

        if self.get_connect_state() == 0:
            self.comm_connect()

    def comm_connect(self):
        self.control.dynamicCall("CommConnect()")
        print('after comm_connect')

    def get_connect_state(self):
        """
        현재 접속상태를 반환합니다.
        반환되는 접속상태는 아래와 같습니다.
        0: 미연결, 1: 연결
        :return: int
        """
        # state = self.control.dynamicCall("GetConnectState()")
        state = self.control.GetConnectState()
        return state