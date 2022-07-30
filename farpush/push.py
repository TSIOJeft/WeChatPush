from itchat.config import PHONE_TYPE
from itchat.config import PUSH_REGID
from itchat.config import BLOCK_NAME
import requests


class farpush:
    def __init__(self):
        self.regid = PUSH_REGID
        self.phone = PHONE_TYPE
        self.block = BLOCK_NAME

    def push(self, title, content):
        # block name
        for check in self.block:
            if check in title:
                return
        data = {
            "content": content,
            "title": title,
            "regID": self.regid,
            'phone': self.phone
        }
        headers = {'content-type': 'application/json'}
        r = requests.post("http://119.3.139.212:9090/PushWeChatMes", data)
