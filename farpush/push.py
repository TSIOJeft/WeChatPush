from itchat.config import PHONE_TYPE
from itchat.config import PUSH_REGID
from itchat.config import BLOCK_NAME
from itchat.config import MES_THROUGH
import requests
import socket
import json

farpush_url = "http://8.147.235.111:9090"



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
        headers = {'content-type': 'application/json'}
        r = requests.post(farpush_url + '/PushWeChatMes', data)

    def mediapush(self, title, content, filename):
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
        resource = {"filename": filename}
        data['resource'] = json.dumps(resource)
        headers = {'content-type': 'application/json'}
        r = requests.post(farpush_url + '/PushWeChatMes', data)
