from ast import In
import os, time, re, io
import json
import mimetypes, hashlib
import logging
from collections import OrderedDict

import requests

from .. import config, utils
from ..returnvalues import ReturnValue
from ..storage import templates
from .contact import update_local_uin

logger = logging.getLogger('itchat')


def load_messages(core):
    core.send_raw_msg = send_raw_msg
    core.send_msg = send_msg
    core.upload_file = upload_file
    core.send_file = send_file
    core.send_image = send_image
    core.send_video = send_video
    core.send = send
    core.revoke = revoke


def get_download_fn(core, url, msgId):
    def download_fn(downloadDir=None):
        params = {
            'msgid': msgId,
            'skey': core.loginInfo['skey'], }
        headers = {'User-Agent': config.USER_AGENT}
        r = core.s.get(url, params=params, stream=True, headers=headers)
        tempStorage = io.BytesIO()
        for block in r.iter_content(1024):
            tempStorage.write(block)
        if downloadDir is None:
            return tempStorage.getvalue()
        with open(downloadDir, 'wb') as f:
            f.write(tempStorage.getvalue())
        tempStorage.seek(0)
        return ReturnValue({'BaseResponse': {
            'ErrMsg': 'Successfully downloaded',
            'Ret': 0, },
            'PostFix': utils.get_image_postfix(tempStorage.read(20)), })

    return download_fn


def produce_msg(core, msgList):
    rl = []
    for m in msgList:
        # get actual opposite
        if m.get('FromUserName') == core.storageClass.userName:
            if config.SELF_MES:
                actualOpposite = m.get('ToUserName')
            else:
                # not send self mes
                continue
        else:
            actualOpposite = m.get('FromUserName')
        # produce basic message
        if '@@' in m.get('FromUserName') or '@@' in m.get('ToUserName'):
            produce_group_chat(core, m)
        else:
            utils.msg_formatter(m, 'Content')
        # set user of msg
        if '@@' in actualOpposite:
            m['User'] = core.search_chatrooms(userName=actualOpposite) or \
                        templates.Chatroom({'UserName': actualOpposite})
            # we don't need to update chatroom here because we have
            # updated once when producing basic message
        elif actualOpposite in ('filehelper', 'fmessage'):
            m['User'] = templates.User({'UserName': actualOpposite})
        else:
            m['User'] = core.search_mps(userName=actualOpposite) or \
                        core.search_friends(userName=actualOpposite) or \
                        templates.User(userName=actualOpposite)
            # by default we think there may be a user missing not a mp
        m['User'].core = core
        msg = {}
        msg['ChatRoom'] = 0
        if m.get('FromUserName') == 'weixin':
            msg['Name'] = msg['NickName'] = '微信团队'
        elif m.get('MsgType') == 37:
            msg['Name'] = msg['NickName'] = m.get('RecommendInfo').get('NickName')
        else:
            Chatroom = '{' + str(''.join(re.findall(r'\[\<ChatroomMember: \{(.*?)\}\>, \<ChatroomMember:', str(m)))) + '}'
            if Chatroom == '{}':
                msg['Name'] = m.get('User').get('NickName') if m.get('User').get('RemarkName') == '' else m.get('User').get('RemarkName')
                msg['NickName'] = m.get('User').get('NickName')
            else:
                if m.get('User').get('ChatRoomOwner') == m.get('ToUserName'):
                    Chatroom = '{' + str(''.join(re.findall(r'\>, \<ChatroomMember: \{(.*?)\}\>\]\>', str(m)))) + '}'
                ChatroomMember = eval(Chatroom.replace('<','\'').replace('>','\''))
                msg['ChatRoom'] = 1
                msg['NickName'] = msg['ChatRoomName'] = m.get('User').get('NickName')
                msg['Name'] = ChatroomMember.get('NickName') if ChatroomMember.get('DisplayName') == '' else ChatroomMember.get('DisplayName')
        if m.get('MsgType') == 1:  # words
            if m.get('Url'):
                msg['Type'] = 'Map'
                msg['Text'] = str(''.join(re.findall(r'poiname="(.*?)" poiid', str(m.get('OriContent')))))
            else:
                msg['Type'] = 'Text'
                msg['Text'] = m.get('Content')
        elif m.get('MsgType') == 3:  # picture
            msg['Type'] = 'Picture'
        elif m.get('MsgType') == 34:  # voice
            msg['Type'] = 'Recording'
        elif m.get('MsgType') == 37:  # friends
            msg['Type'] = 'Friends'
        elif m.get('MsgType') == 42:  # name card
            msg['Type'] = 'Card'
            msg['Text'] = m.get('RecommendInfo').get('NickName')
        elif m.get('MsgType') in (43, 62):  # tiny video
            msg['Type'] = 'Video'
        elif m.get('MsgType') == 47:  # emoti_con
            msg['Type'] = 'Emoticon'
        elif m.get('MsgType') == 48:
            msg['Type'] = 'Location'
        elif m.get('MsgType') == 49:  # sharing
            if m.get('FromUserName') == 'weixin':
                msg['Type'] = 'Servicenotification'
                msg['Text'] = m.get('FileName')
            elif msg.get('Name') == None:
                msg['Name'] = msg['NickName'] = '服务通知'
                msg['Type'] = 'Servicenotification'
                msg['Text'] = m.get('FileName')
            elif m.get('AppMsgType') == 0:  # chat history
                msg['Type'] = 'Chathistory'
            elif m.get('AppMsgType') == 3:
                msg['Type'] = 'Musicshare'
                msg['Text'] = m.get('FileName')
            elif m.get('AppMsgType') == 5:
                msg['Type'] = 'Webshare'
                msg['Text'] = m.get('FileName')
            elif m.get('AppMsgType') == 6:
                msg['Type'] = 'Attachment'
                msg['Text'] = m.get('FileName')
            elif m.get('AppMsgType') == 8:
                msg['Type'] = 'Picture'
            elif m.get('AppMsgType') == 17:
                msg['Type'] = 'Locationshare'
                msg['Text'] = m.get('FileName')
            elif m.get('AppMsgType') == 33:
                msg['Type'] = 'Miniprogram'
                msg['Text'] = m.get('FileName')
            elif m.get('AppMsgType') == 2000:
                msg['Type'] = 'Transfer'
            else:
                msg['Type'] = 'Sharing'
                msg['Text'] = m.get('AppMsgType')
        elif m.get('MsgType') in (50, 52, 53): # voip
            msg['Type'] = 'Voip'
        elif m.get('MsgType') == 51:  # phone init
            msg = update_local_uin(core, m)
        elif m.get('MsgType') == 10000:
            if m.get('Content') == '收到红包，请在手机上查看':
                msg['Type'] = 'Redenvelope'
            elif m.get('Content') == '群收款消息，请在手机上查看':
                msg['Type'] = 'Splitthebill'
            elif m.get('Content') == '你的微信版本较低，升级微信体验多人语音通话。':
                msg['Type'] = 'Voip'
            else:
                msg['Type'] = 'Systemnotification'
        elif m.get('MsgType') == 10002:
            msg['Type'] = 'Recalled'
        elif m.get('MsgType') in (40, 9999):
            msg['Type'] = 'Useless'
            msg['Text'] = 'UselessMsg'
        else:
            msg['Type'] = 'Undefined'
            msg['Text'] = m.get('MsgType')
        m = dict(m, **msg)
        rl.append(m)
    return rl


def produce_group_chat(core, msg):
    r = re.match('(@[0-9a-z]*?):<br/>(.*)$', msg['Content'])
    if r:
        actualUserName, content = r.groups()
        chatroomUserName = msg['FromUserName']
    elif msg['FromUserName'] == core.storageClass.userName:
        actualUserName = core.storageClass.userName
        content = msg['Content']
        chatroomUserName = msg['ToUserName']
    else:
        msg['ActualUserName'] = core.storageClass.userName
        msg['ActualNickName'] = core.storageClass.nickName
        msg['IsAt'] = False
        utils.msg_formatter(msg, 'Content')
        return
    chatroom = core.storageClass.search_chatrooms(userName=chatroomUserName)
    member = utils.search_dict_list((chatroom or {}).get(
        'MemberList') or [], 'UserName', actualUserName)
    if member is None:
        chatroom = core.update_chatroom(chatroomUserName)
        member = utils.search_dict_list((chatroom or {}).get(
            'MemberList') or [], 'UserName', actualUserName)
    if member is None:
        logger.debug('chatroom member fetch failed with %s' % actualUserName)
        msg['ActualNickName'] = ''
        msg['IsAt'] = False
    else:
        msg['ActualNickName'] = member.get('DisplayName', '') or member['NickName']
        atFlag = '@' + (chatroom['Self'].get('DisplayName', '') or core.storageClass.nickName)
        msg['IsAt'] = (
                (atFlag + (u'\u2005' if u'\u2005' in msg['Content'] else ' '))
                in msg['Content'] or msg['Content'].endswith(atFlag))
    msg['ActualUserName'] = actualUserName
    msg['Content'] = content
    utils.msg_formatter(msg, 'Content')


def send_raw_msg(self, msgType, content, toUserName):
    url = '%s/webwxsendmsg' % self.loginInfo['url']
    data = {
        'BaseRequest': self.loginInfo['BaseRequest'],
        'Msg': {
            'Type': msgType,
            'Content': content,
            'FromUserName': self.storageClass.userName,
            'ToUserName': (toUserName if toUserName else self.storageClass.userName),
            'LocalID': int(time.time() * 1e4),
            'ClientMsgId': int(time.time() * 1e4),
        },
        'Scene': 0, }
    headers = {'ContentType': 'application/json; charset=UTF-8', 'User-Agent': config.USER_AGENT}
    r = self.s.post(url, headers=headers,
                    data=json.dumps(data, ensure_ascii=False).encode('utf8'))
    return ReturnValue(rawResponse=r)


def send_msg(self, msg='Test Message', toUserName=None):
    logger.debug('Request to send a text message to %s: %s' % (toUserName, msg))
    r = self.send_raw_msg(1, msg, toUserName)
    return r


def _prepare_file(fileDir, file_=None):
    fileDict = {}
    if file_:
        if hasattr(file_, 'read'):
            file_ = file_.read()
        else:
            return ReturnValue({'BaseResponse': {
                'ErrMsg': 'file_ param should be opened file',
                'Ret': -1005, }})
    else:
        if not utils.check_file(fileDir):
            return ReturnValue({'BaseResponse': {
                'ErrMsg': 'No file found in specific dir',
                'Ret': -1002, }})
        with open(fileDir, 'rb') as f:
            file_ = f.read()
    fileDict['fileSize'] = len(file_)
    fileDict['fileMd5'] = hashlib.md5(file_).hexdigest()
    fileDict['file_'] = io.BytesIO(file_)
    return fileDict


def upload_file(self, fileDir, isPicture=False, isVideo=False,
                toUserName='filehelper', file_=None, preparedFile=None):
    logger.debug('Request to upload a %s: %s' % (
        'picture' if isPicture else 'video' if isVideo else 'file', fileDir))
    if not preparedFile:
        preparedFile = _prepare_file(fileDir, file_)
        if not preparedFile:
            return preparedFile
    fileSize, fileMd5, file_ = \
        preparedFile['fileSize'], preparedFile['fileMd5'], preparedFile['file_']
    fileSymbol = 'pic' if isPicture else 'video' if isVideo else 'doc'
    chunks = int((fileSize - 1) / 524288) + 1
    clientMediaId = int(time.time() * 1e4)
    uploadMediaRequest = json.dumps(OrderedDict([
        ('UploadType', 2),
        ('BaseRequest', self.loginInfo['BaseRequest']),
        ('ClientMediaId', clientMediaId),
        ('TotalLen', fileSize),
        ('StartPos', 0),
        ('DataLen', fileSize),
        ('MediaType', 4),
        ('FromUserName', self.storageClass.userName),
        ('ToUserName', toUserName),
        ('FileMd5', fileMd5)]
    ), separators=(',', ':'))
    r = {'BaseResponse': {'Ret': -1005, 'ErrMsg': 'Empty file detected'}}
    for chunk in range(chunks):
        r = upload_chunk_file(self, fileDir, fileSymbol, fileSize,
                              file_, chunk, chunks, uploadMediaRequest)
    file_.close()
    if isinstance(r, dict):
        return ReturnValue(r)
    return ReturnValue(rawResponse=r)


def upload_chunk_file(core, fileDir, fileSymbol, fileSize,
                      file_, chunk, chunks, uploadMediaRequest):
    url = core.loginInfo.get('fileUrl', core.loginInfo['url']) + \
          '/webwxuploadmedia?f=json'
    # save it on server
    cookiesList = {name: data for name, data in core.s.cookies.items()}
    fileType = mimetypes.guess_type(fileDir)[0] or 'application/octet-stream'
    fileName = utils.quote(os.path.basename(fileDir))
    files = OrderedDict([
        ('id', (None, 'WU_FILE_0')),
        ('name', (None, fileName)),
        ('type', (None, fileType)),
        ('lastModifiedDate', (None, time.strftime('%a %b %d %Y %H:%M:%S GMT+0800 (CST)'))),
        ('size', (None, str(fileSize))),
        ('chunks', (None, None)),
        ('chunk', (None, None)),
        ('mediatype', (None, fileSymbol)),
        ('uploadmediarequest', (None, uploadMediaRequest)),
        ('webwx_data_ticket', (None, cookiesList['webwx_data_ticket'])),
        ('pass_ticket', (None, core.loginInfo['pass_ticket'])),
        ('filename', (fileName, file_.read(524288), 'application/octet-stream'))])
    if chunks == 1:
        del files['chunk'];
        del files['chunks']
    else:
        files['chunk'], files['chunks'] = (None, str(chunk)), (None, str(chunks))
    headers = {'User-Agent': config.USER_AGENT}
    return core.s.post(url, files=files, headers=headers, timeout=config.TIMEOUT)


def send_file(self, fileDir, toUserName=None, mediaId=None, file_=None):
    logger.debug('Request to send a file(mediaId: %s) to %s: %s' % (
        mediaId, toUserName, fileDir))
    if hasattr(fileDir, 'read'):
        return ReturnValue({'BaseResponse': {
            'ErrMsg': 'fileDir param should not be an opened file in send_file',
            'Ret': -1005, }})
    if toUserName is None:
        toUserName = self.storageClass.userName
    preparedFile = _prepare_file(fileDir, file_)
    if not preparedFile:
        return preparedFile
    fileSize = preparedFile['fileSize']
    if mediaId is None:
        r = self.upload_file(fileDir, preparedFile=preparedFile)
        if r:
            mediaId = r['MediaId']
        else:
            return r
    url = '%s/webwxsendappmsg?fun=async&f=json' % self.loginInfo['url']
    data = {
        'BaseRequest': self.loginInfo['BaseRequest'],
        'Msg': {
            'Type': 6,
            'Content': ("<appmsg appid='wxeb7ec651dd0aefa9' sdkver=''><title>%s</title>" % os.path.basename(fileDir) +
                        "<des></des><action></action><type>6</type><content></content><url></url><lowurl></lowurl>" +
                        "<appattach><totallen>%s</totallen><attachid>%s</attachid>" % (str(fileSize), mediaId) +
                        "<fileext>%s</fileext></appattach><extinfo></extinfo></appmsg>" % os.path.splitext(fileDir)[
                            1].replace('.', '')),
            'FromUserName': self.storageClass.userName,
            'ToUserName': toUserName,
            'LocalID': int(time.time() * 1e4),
            'ClientMsgId': int(time.time() * 1e4), },
        'Scene': 0, }
    headers = {
        'User-Agent': config.USER_AGENT,
        'Content-Type': 'application/json;charset=UTF-8', }
    r = self.s.post(url, headers=headers,
                    data=json.dumps(data, ensure_ascii=False).encode('utf8'))
    return ReturnValue(rawResponse=r)


def send_image(self, fileDir=None, toUserName=None, mediaId=None, file_=None):
    logger.debug('Request to send a image(mediaId: %s) to %s: %s' % (
        mediaId, toUserName, fileDir))
    if fileDir or file_:
        if hasattr(fileDir, 'read'):
            file_, fileDir = fileDir, None
        if fileDir is None:
            fileDir = 'tmp.jpg'  # specific fileDir to send gifs
    else:
        return ReturnValue({'BaseResponse': {
            'ErrMsg': 'Either fileDir or file_ should be specific',
            'Ret': -1005, }})
    if toUserName is None:
        toUserName = self.storageClass.userName
    if mediaId is None:
        r = self.upload_file(fileDir, isPicture=not fileDir[-4:] == '.gif', file_=file_)
        if r:
            mediaId = r['MediaId']
        else:
            return r
    url = '%s/webwxsendmsgimg?fun=async&f=json' % self.loginInfo['url']
    data = {
        'BaseRequest': self.loginInfo['BaseRequest'],
        'Msg': {
            'Type': 3,
            'MediaId': mediaId,
            'FromUserName': self.storageClass.userName,
            'ToUserName': toUserName,
            'LocalID': int(time.time() * 1e4),
            'ClientMsgId': int(time.time() * 1e4), },
        'Scene': 0, }
    if fileDir[-4:] == '.gif':
        url = '%s/webwxsendemoticon?fun=sys' % self.loginInfo['url']
        data['Msg']['Type'] = 47
        data['Msg']['EmojiFlag'] = 2
    headers = {
        'User-Agent': config.USER_AGENT,
        'Content-Type': 'application/json;charset=UTF-8', }
    r = self.s.post(url, headers=headers,
                    data=json.dumps(data, ensure_ascii=False).encode('utf8'))
    return ReturnValue(rawResponse=r)


def send_video(self, fileDir=None, toUserName=None, mediaId=None, file_=None):
    logger.debug('Request to send a video(mediaId: %s) to %s: %s' % (
        mediaId, toUserName, fileDir))
    if fileDir or file_:
        if hasattr(fileDir, 'read'):
            file_, fileDir = fileDir, None
        if fileDir is None:
            fileDir = 'tmp.mp4'  # specific fileDir to send other formats
    else:
        return ReturnValue({'BaseResponse': {
            'ErrMsg': 'Either fileDir or file_ should be specific',
            'Ret': -1005, }})
    if toUserName is None:
        toUserName = self.storageClass.userName
    if mediaId is None:
        r = self.upload_file(fileDir, isVideo=True, file_=file_)
        if r:
            mediaId = r['MediaId']
        else:
            return r
    url = '%s/webwxsendvideomsg?fun=async&f=json&pass_ticket=%s' % (
        self.loginInfo['url'], self.loginInfo['pass_ticket'])
    data = {
        'BaseRequest': self.loginInfo['BaseRequest'],
        'Msg': {
            'Type': 43,
            'MediaId': mediaId,
            'FromUserName': self.storageClass.userName,
            'ToUserName': toUserName,
            'LocalID': int(time.time() * 1e4),
            'ClientMsgId': int(time.time() * 1e4), },
        'Scene': 0, }
    headers = {
        'User-Agent': config.USER_AGENT,
        'Content-Type': 'application/json;charset=UTF-8', }
    r = self.s.post(url, headers=headers,
                    data=json.dumps(data, ensure_ascii=False).encode('utf8'))
    return ReturnValue(rawResponse=r)


def send(self, msg, toUserName=None, mediaId=None):
    if not msg:
        r = ReturnValue({'BaseResponse': {
            'ErrMsg': 'No message.',
            'Ret': -1005, }})
    elif msg[:5] == '@fil@':
        if mediaId is None:
            r = self.send_file(msg[5:], toUserName)
        else:
            r = self.send_file(msg[5:], toUserName, mediaId)
    elif msg[:5] == '@img@':
        if mediaId is None:
            r = self.send_image(msg[5:], toUserName)
        else:
            r = self.send_image(msg[5:], toUserName, mediaId)
    elif msg[:5] == '@msg@':
        r = self.send_msg(msg[5:], toUserName)
    elif msg[:5] == '@vid@':
        if mediaId is None:
            r = self.send_video(msg[5:], toUserName)
        else:
            r = self.send_video(msg[5:], toUserName, mediaId)
    else:
        r = self.send_msg(msg, toUserName)
    return r


def revoke(self, msgId, toUserName, localId=None):
    url = '%s/webwxrevokemsg' % self.loginInfo['url']
    data = {
        'BaseRequest': self.loginInfo['BaseRequest'],
        "ClientMsgId": localId or str(time.time() * 1e3),
        "SvrMsgId": msgId,
        "ToUserName": toUserName}
    headers = {
        'ContentType': 'application/json; charset=UTF-8',
        'User-Agent': config.USER_AGENT}
    r = self.s.post(url, headers=headers,
                    data=json.dumps(data, ensure_ascii=False).encode('utf8'))
    return ReturnValue(rawResponse=r)
