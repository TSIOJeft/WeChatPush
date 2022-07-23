import requests
import itchat
import itchat.content
import itchat.config
import farpush


@itchat.msg_register(itchat.content.TEXT)
def text_reply(msg):
    print(msg.user.nickName + " say : " + msg.text)
    farpush.mespush(msg.user.nickName, msg.text)


@itchat.msg_register(itchat.content.TEXT, isGroupChat=True)
def text_reply(msg):
    farpush.mespush(msg.user.nickName, msg.text)


if __name__ == '__main__':
    itchat.check_login()
    itchat.auto_login(hotReload=True,enableCmdQR=2)
    itchat.run()
