TEXT = 'Text'  # 文本
CARD = 'Card'  # 好友名片、公众号名片
SHARING = 'Sharing'  # 未知卡片消息
PICTURE = 'Picture'  # 图片
EMOTICON = 'Emoticon'  # 动画表情
RECORDING = 'Recording'  # 语音
ATTACHMENT = 'Attachment'  # 文件
WEBSHARE = 'Webshare'  # 网页分享
SPLITTHEBILL = 'Splitthebill' #群收款
VIDEO = 'Video'  # 视频
VOIP = 'Voip'  # 通话邀请
FRIENDS = 'Friends'  # 好友请求
MUSICSHARE = 'Musicshare'  # 音乐分享
LOCATIONSHARE = 'Locationshare'  # 共享实时位置
MAP = 'Map'  # 位置分享
SERVICENOTIFICATION = 'Servicenotification'  # 服务通知
RECALLED = 'Recalled'  # 撤回提醒
MINIPROGRAM = 'Miniprogram'  # 小程序分享
CHATHISTORY = 'Chathistory'  # 聊天记录
TRANSFER = 'Transfer'  # 转账
REDENVELOPE = 'Redenvelope'  # 红包
SYSTEMNOTIFICATION = 'Systemnotification'  # 系统消息
UNDEFINED = 'Undefined'  # 未知消息类型

INCOME_MSG = [TEXT, CARD, SHARING, PICTURE, EMOTICON, RECORDING, ATTACHMENT, WEBSHARE, SPLITTHEBILL,
              VIDEO, VOIP, FRIENDS, MUSICSHARE, LOCATIONSHARE, MAP, SERVICENOTIFICATION, RECALLED,
              MINIPROGRAM, CHATHISTORY, TRANSFER, REDENVELOPE, UNDEFINED, SYSTEMNOTIFICATION]

MEDIA_TYPE_MSG = [
    CARD, SHARING, PICTURE, EMOTICON, RECORDING, ATTACHMENT, WEBSHARE, SPLITTHEBILL,
    VIDEO, VOIP, FRIENDS, MUSICSHARE, LOCATIONSHARE, MAP, SERVICENOTIFICATION,
    MINIPROGRAM, CHATHISTORY, TRANSFER, REDENVELOPE, UNDEFINED, SYSTEMNOTIFICATION
]

MESSAGE_TEXT = {
    TEXT: '文字',
    MAP: '地图分享',
    PICTURE: '图片',
    SHARING: '分享',
    RECORDING: '语音',
    ATTACHMENT: '文件',
    VIDEO: '视频',
    FRIENDS: '好友请求',
    VOIP: '音视频邀请',
    SERVICENOTIFICATION: '服务提醒',
    WEBSHARE: '网页分享',
    SPLITTHEBILL: '群收款',
    TRANSFER: '转账',
    REDENVELOPE: '红包',
    MINIPROGRAM: '小程序分享',
    CHATHISTORY: '聊天记录',
    UNDEFINED: '未知类型',
    CARD: '名片',
    EMOTICON: '动画表情',
    FRIENDS: '好友请求',
    MUSICSHARE: '音乐分享',
    LOCATIONSHARE: '共享实时位置'

}
