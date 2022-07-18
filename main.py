import requests

import itchat
import itchat.content
import itchat.config


@itchat.msg_register(itchat.content.TEXT)
def text_reply(msg):
    print(msg.user.nickName+"说:"+msg.text)
    data = {
        "content": msg.text,
        "title": msg.user.nickName,
        "regID": itchat.config.PUSH_REGID,
        'phone': itchat.config.PHONE_TYPE
    }
    headers = {'content-type': 'application/json'}
    r = requests.post("http://119.3.139.212:9090/PushWeChatMes", data)


@itchat.msg_register(itchat.content.TEXT, isGroupChat=True)
def text_reply(msg):
    data = {
        "content": msg.text,
        "title": msg.user.nickName,
        "regID": itchat.config.PUSH_REGID,
        'phone': itchat.config.PHONE_TYPE
    }
    headers = {'content-type': 'application/json'}
    r = requests.post("http://119.3.139.212:9090/PushWeChatMes", data)


if __name__ == '__main__':
    itchat.check_login()
    itchat.auto_login(hotReload=True,enableCmdQR=2)
    itchat.run()
