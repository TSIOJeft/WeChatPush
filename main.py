import requests
from flask import Flask, request, jsonify
from gevent import pywsgi
import itchat
import itchat.content
import itchat.config
import farpush
import socket
import json
import _thread

app = Flask(__name__)


@app.route("/send", methods=['POST'])
def received():
    data = request.json
    username = data['username']
    nametype = data['type']
    content = data['content']
    if nametype == '0':
        send4nick(username, content)
    else:
        send(username, content)
    return 'ok'


@itchat.msg_register(itchat.content.TEXT)
def text_reply(msg):
    print(msg.user.nickName + " say : " + msg.text)
    farpush.mespush(msg.user.nickName, msg.text)


@itchat.msg_register([itchat.content.VOICE, itchat.content.PICTURE, itchat.content.VIDEO])
def text_reply(msg):
    farpush.mespush(msg.user.nickName, msg.type)


@itchat.msg_register(itchat.content.TEXT, isGroupChat=True)
def text_reply(msg):
    farpush.mespush(msg.user.nickName, msg.text)


def send(username, content):
    itchat.send(content, toUserName=username)


def send4nick(nickname, content):
    friends = itchat.search_friends(nickName=nickname)
    if friends:
        author = friends[0]
        author.send(content)


def flask(ip, port):
    server = pywsgi.WSGIServer((ip, port), app)
    server.serve_forever()


if __name__ == '__main__':
    _thread.start_new_thread(flask, ('0.0.0.0', 9091))
    itchat.check_login()
    itchat.auto_login(hotReload=True, enableCmdQR=2)
    itchat.run()
