from itchat.config import PHONE_TYPE
from itchat.config import PUSH_REGID
from itchat.config import BLOCK_NAME
from itchat.config import MES_THROUGH
import requests
import socket
import json


class farpush:
    def __init__(self):
        self.regid = PUSH_REGID
        self.phone = PHONE_TYPE
        self.block = BLOCK_NAME
        self.through = MES_THROUGH

    def push(self, title, content):
        # block name
        for check in self.block:
            if check in title:
                return
        data = {
            "content": content,
            "title": title,
            "regID": self.regid,
            'phone': self.phone,
            'through': self.through
        }
        # if self.phone == 4:
        #     hw = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        #     data = {'title': title, 'content': content}
        #     hw.sendto(json.dumps(data).encode("GBK"), (SOCKET_IP, SOCKET_PORT))
        #     hw.close()
        #     return
        headers = {'content-type': 'application/json'}
        r = requests.post("http://119.3.139.212:9090/PushWeChatMes", data)
