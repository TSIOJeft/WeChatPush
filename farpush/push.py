from itchat.config import PHONE_TYPE
from itchat.config import PUSH_REGID
import requests


class farpush:
    def __init__(self):
        self.regid = PUSH_REGID
        self.phone = PHONE_TYPE

    def push(self, title, content):
        data = {
            "content": content,
            "title": title,
            "regID": self.regid,
            'phone': self.phone
        }
        headers = {'content-type': 'application/json'}
        r = requests.post("http://119.3.139.212:9090/PushWeChatMes", data)
