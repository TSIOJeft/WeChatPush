# WeChatPush

基于itchat的微信消息接收端 感谢itchat大佬 和itchat-uos

在itchat 基础上修复一些问题

[itchat](https://github.com/littlecodersh/ItChat)

[itchat-uos](https://github.com/why2lyj/ItChat-UOS)

### 怎样使用？

下载或者克隆这个项目 

然后导入相关库 

修改 itchat/config 内的 设备ID 和phone 类型

phont类型中 0对应小米 1对应oppo 2对应华为 4对应腾讯推送 3对应fcm (目前服务器不支持) 5 对应bark

不接收的消息来自用户名 写在itchat/config BLOCK_NAME 数组里 包含关系 只需要输入前几位就行

目前mipush 腾讯云推送 支持直接回复 腾讯云需要在itchat/config 里的 MES_THROUGH 改为 1 

快速回复需要在FarPush 快速回复里填写你的服务器地址 

像这样 http://192.168.0.1:9091/send

这样的话FarPush 在接收到消息 会发送支持回复的通知 然后通知你的服务器 发送消息 用的是python flask 端口默认在9091 可能需要您开启防火墙 或者自行更改端口

快速查看语音 或者图片 请在快速回复里填入你的服务器地址 http://192.168.0.1:9091/send 这样 后面的/send 不影响 会自动处理
存储的文件在 files 文件夹内 FarPush 存储在 /storage/emulated/0/android/data/com.farplace.qingzhuo/files/media 内

如果window 等需要使用图片请在main.py 里 itchat 参数内删掉 enablecmdqr

最后后台运行 请使用 nohup python3 main.py& tail -f nohup.out

[FarPush](www.coolapk.com/apk/com.farplace.farpush)

#### FarPush 交流群 833957139

导入库 pip3 install -r requirements.txt

感谢分支 [WeChatPush](https://github.com/IlineI/WeChatPush) 消息的更多完善感谢@chase355 感谢

CentOS 还需要 yum install xdg-utils

#### 2024/9/21

新的服务器买好了一年期限 
