# coding=utf-8
"""
插件开发模板

我一个人开发此项目难免有些疏漏，所以请积极发issue、提交pull request哦！感谢大家帮助完善这个项目！
"""
import py_xlz_http as xlz


@xlz.private_msg_handler()
def private(message: xlz.types.PrivateMsg):
    # 自己在其他设备向别人发送消息时：数据.来源事件QQ 为收信QQ   数据.来源事件QQ昵称 为收信QQ昵称
    # 分片消息也将传入插件，方便进行撤回消息，如果你不需要分片消息，可以过滤掉分片消息
    # 当你未使用框架发送过匿名消息时，其他设备发送匿名消息，数据.框架QQ匿名Id=0，此时，可以使用API【强制取自身匿名Id】解决问题
    # 返回 True 拦截其他处理函数继续处理该消息

    if not message.from_qq.qq == message.logon_qq:  # 过滤自己(包括其他设备)的消息，你也可以不过滤

        if message.msg.type == xlz.types.MessageTypes.临时会话.value:

            if message.msg.subtype_temp == xlz.types.MessageTypes.临时会话_群临时.value:
                pass

            elif message.msg.subtype_temp == xlz.types.MessageTypes.临时会话_讨论组临时.value:
                pass

            elif message.msg.subtype_temp == xlz.types.MessageTypes.临时会话_公众号.value:
                pass

            elif message.msg.subtype_temp == xlz.types.MessageTypes.临时会话_网页QQ咨询.value:
                pass

        elif message.msg.type == xlz.types.MessageTypes.好友消息.value:
            # 在付费版本当中，真正的红包等将传入文本代码，直接发送红包等的代码将被框架转义，再传入，所以不用担心安全问题
            # 需要注意的是，当框架QQ未实名认证时，转账无法自动到账，将是这样的：[transfer,title=请点击收款,memo=QQ转账,transId=101000026901302104201398395831]
            # 所以当 title = 请点击收款 时，请注意，此时转账并未到账
            pass


@xlz.group_msg_handler()
def group(message: xlz.types.GroupMsg):
    # 分片消息也将传入插件，方便进行撤回消息，如果你不需要分片消息，可以过滤掉分片消息
    # 当你的插件需要弹框时，请在信息框标题注明这个弹框来自于哪个插件，以免对用户造成困扰
    # 当你未使用框架发送过匿名消息时，其他设备发送匿名消息，数据.框架QQ匿名Id=0，此时，可以使用API【强制取自身匿名Id】解决问题
    # 返回 True 拦截其他处理函数继续处理该消息

    if message.from_qq.qq != message.logon_qq and message.from_qq.qq != message.logon_qq_anonymous_id:  # 过滤自己(包括其他设备)的消息，你也可以不过滤
        # 在付费版本当中，真正的红包等将传入文本代码，直接发送红包等的代码将被框架转义，再传入，所以不用担心安全问题

        if message.msg.subtype == xlz.types.MessageTypes.讨论组消息.value:
            # 讨论组消息处理
            pass

        else:
            # 群聊消息处理
            pass


@xlz.event_msg_handler()
def event(message: xlz.types.EventMsg):
    if message.msg.type == xlz.types.EventTypes.好友事件_签名变更.value:
        # message.logon_qq 框架QQ
        # message.from_qq.qq 签名变更的QQ
        # message.msg.timestamp 现在的时间
        # message.operate_qq.nickname 新的签名内容
        # message.from_qq.nickname 变更QQ的昵称
        pass

    elif message.msg.type == xlz.types.EventTypes.好友事件_昵称改变.value:
        # message.logon_qq 框架QQ
        # message.from_qq.qq 昵称变更的QQ
        # message.msg.timestamp 现在的时间
        # message.from_qq.nickname 新的昵称内容
        pass

    elif message.msg.type == xlz.types.EventTypes.好友事件_有新好友.value:
        # message.logon_qq 框架QQ
        # message.from_qq.qq 新好友的QQ
        # message.msg.timestamp 现在的时间
        # message.from_qq.nickname 新好友的昵称
        pass

    elif message.msg.type == xlz.types.EventTypes.好友事件_好友请求.value:
        # message.logon_qq 框架QQ
        # message.from_qq.qq 对方QQ
        # message.from_qq.nickname 对方QQ昵称
        # message.msg.subtype 为1：被添加为单向好友,为2：请求添加为好友
        # message.msg.text 验证消息
        pass

    elif message.msg.type == xlz.types.EventTypes.好友事件_被好友删除.value:
        # message.logon_qq 框架QQ
        # message.from_qq.qq  删除者QQ
        # message.msg.timestamp 现在的时间
        # message.from_qq.nickname 删除者QQ昵称
        pass

    elif message.msg.type == xlz.types.EventTypes.好友事件_某人撤回事件.value:  # 讨论组临时消息撤回事件、群临时消息撤回事件也被包含在内
        # message.logon_qq 框架QQ
        # message.from_qq.qq  撤回者QQ
        # message.msg.seq 可用于取缓存消息
        # message.msg.timestamp 撤回消息发送时间
        # message.from_qq.nickname 撤回者QQ昵称
        # message.msg.text 撤回消息内容
        pass

    elif message.msg.type == xlz.types.EventTypes.好友事件_对方同意了您的好友请求.value:
        # message.logon_qq 框架QQ
        # message.from_qq.qq 同意者QQ
        # message.msg.timestamp 同意时间
        # message.from_qq.nickname 同意者QQ昵称
        pass

    elif message.msg.type == xlz.types.EventTypes.好友事件_对方拒绝了您的好友请求.value:
        # message.logon_qq 框架QQ
        # message.from_qq.qq 拒绝者QQ
        # message.msg.timestamp 拒绝时间
        # message.from_qq.nickname 拒绝者昵称
        pass

    elif message.msg.type == xlz.types.EventTypes.好友事件_资料卡点赞.value:
        # message.logon_qq 框架QQ
        # message.from_qq.qq  点赞者QQ
        # message.msg.timestamp 点赞时间
        # message.from_qq.nickname 点赞者QQ昵称
        # message.msg.text 点赞事件文本
        pass

    elif message.msg.type == xlz.types.EventTypes.好友事件_签名点赞.value:
        # message.logon_qq 框架QQ
        # message.from_qq.qq  点赞者QQ
        # message.msg.timestamp 点赞时间
        # message.from_qq.nickname 点赞者QQ昵称
        # message.msg.text 点赞事件文本
        # message.operate_qq.nickname 签名内容
        pass

    elif message.msg.type == xlz.types.EventTypes.好友事件_签名回复.value:
        # message.logon_qq 框架QQ
        # message.from_qq.qq  回复者QQ
        # message.msg.timestamp 回复时间
        # message.from_qq.nickname 回复者QQ昵称
        # message.msg.text 回复内容
        # message.operate_qq.nickname 签名内容
        pass

    elif message.msg.type == xlz.types.EventTypes.好友事件_个性标签点赞.value:
        # message.logon_qq 框架QQ
        # message.from_qq.qq  点赞者QQ
        # message.msg.timestamp 点赞时间
        # message.from_qq.nickname 点赞者QQ昵称
        # message.msg.text 点赞事件文本
        # message.operate_qq.nickname 个性标签内容
        pass

    elif message.msg.type == xlz.types.EventTypes.好友事件_随心贴回复.value:
        # message.logon_qq 框架QQ
        # message.from_qq.qq  回复者QQ
        # message.operate_qq.qq 随心贴发送者QQ
        # message.msg.timestamp 回复时间
        # message.from_group.name 随心贴内容
        # message.from_qq.nickname 回复者QQ昵称
        # message.operate_qq.nickname 随心贴发送者QQ昵称
        # message.msg.text 回复内容
        pass

    elif message.msg.type == xlz.types.EventTypes.好友事件_随心贴增添.value:
        # message.logon_qq 框架QQ
        # message.from_qq.qq  增添者QQ
        # message.msg.timestamp 增添时间
        # message.from_qq.nickname 增添者QQ昵称
        # message.msg.text 增添事件文本
        # message.operate_qq.nickname 随心贴内容
        pass

    elif message.msg.type == xlz.types.EventTypes.好友事件_系统提示.value:
        # message.logon_qq 框架QQ
        # message.from_qq.qq 提示触发者QQ
        # message.from_qq.nickname 提示触发者QQ昵称
        # message.msg.text QQ系统提示数据
        pass

    elif message.msg.type == xlz.types.EventTypes.好友事件_随心贴点赞.value:
        # message.logon_qq 框架QQ
        # message.from_qq.qq  点赞QQ
        # message.operate_qq.qq 随心贴留言者QQ
        # message.msg.timestamp 点赞时间
        # message.from_qq.nickname 点赞QQ昵称
        # message.operate_qq.nickname 随心贴留言者QQ昵称
        # message.msg.text 随心贴内容
        pass

    elif message.msg.type == xlz.types.EventTypes.好友事件_匿名提问_被提问.value:
        # message.logon_qq 框架QQ
        # message.from_qq.qq  提问者QQ
        # message.msg.timestamp 提问时间
        # message.from_qq.nickname 提问者QQ昵称
        # message.msg.text 提问事件文本
        pass

    elif message.msg.type == xlz.types.EventTypes.好友事件_匿名提问_被点赞.value:
        # message.logon_qq 框架QQ
        # message.from_qq.qq  点赞者QQ
        # message.msg.timestamp 点赞时间
        # message.from_qq.nickname 点赞者QQ昵称
        # message.msg.text 点赞事件文本
        # message.operate_qq.nickname 提问内容
        pass

    elif message.msg.type == xlz.types.EventTypes.好友事件_匿名提问_被回复.value:
        # message.logon_qq 框架QQ
        # message.from_qq.qq  回复者QQ
        # message.msg.timestamp 回复时间
        # message.from_qq.nickname 回复者QQ昵称
        # message.msg.text 回复内容
        # message.operate_qq.nickname 提问内容
        pass

    elif message.msg.type == xlz.types.EventTypes.好友事件_输入状态.value:
        # message.logon_qq 框架QQ
        # message.from_qq.qq  好友QQ
        # message.msg.timestamp 触发时间戳
        # message.from_qq.nickname 好友QQ昵称
        # message.msg.text 输入状态文本
        pass

    elif message.msg.type == xlz.types.EventTypes.群事件_群被解散.value:
        # message.logon_qq 框架QQ
        # message.from_group.group 解散群号
        # message.msg.timestamp  解散时间
        # message.from_group.name 解散群名
        # message.operate_qq.qq、message.from_qq.qq 解散者QQ
        # message.operate_qq.nickname、message.from_qq.nickname 解散者QQ昵称
        pass

    elif message.msg.type == xlz.types.EventTypes.群事件_某人被禁言.value:
        # message.logon_qq 框架QQ
        # message.from_group.group 事件群号
        # message.operate_qq.qq 禁言者QQ
        # message.from_qq.qq 被禁者QQ
        # message.msg.seq 被禁秒数
        # message.msg.timestamp 被禁时间
        # message.from_group.name 事件群名
        # message.operate_qq.nickname 禁言者QQ昵称
        # message.from_qq.nickname 被禁者QQ昵称
        pass

    elif message.msg.type == xlz.types.EventTypes.群事件_某人被解除禁言.value:
        # message.logon_qq 框架QQ
        # message.from_group.group 事件群号
        # message.operate_qq.qq 解除者QQ
        # message.from_qq.qq 被解除者QQ(首个)
        # message.msg.timestamp 被解除时间
        # message.from_group.name 事件群名
        # message.operate_qq.nickname 解除者QQ昵称
        # message.from_qq.nickname 被解除者QQ昵称(首个)
        # message.msg.text 当事件为批量解除禁言事件时,此处返回被解除禁言的QQ列表(以|号分隔),如:10001|10002|10003
        pass

    elif message.msg.type == xlz.types.EventTypes.群事件_匿名被禁言.value:
        # message.logon_qq 框架QQ
        # message.from_group.group 事件群号
        # message.operate_qq.qq 禁言者QQ
        # message.msg.seq被禁秒数
        # message.msg.timestamp 被禁时间
        # message.from_group.name 事件群名
        # message.operate_qq.nickname 禁言者QQ昵称
        # message.from_qq.nickname 被禁者匿名
        pass

    elif message.msg.type == xlz.types.EventTypes.群事件_匿名被解除禁言.value:
        # message.logon_qq 框架QQ
        # message.from_group.group 事件群号
        # message.operate_qq.qq 解除者QQ
        # message.msg.timestamp 被解除时间
        # message.from_group.name 事件群名
        # message.operate_qq.nickname 解除者QQ昵称
        # message.from_qq.nickname 被解除者匿名
        pass

    elif message.msg.type == xlz.types.EventTypes.群事件_某人加入了群.value:
        # message.logon_qq 框架QQ
        # message.from_group.group 事件群号
        # message.operate_qq.qq 审批者QQ
        # message.msg.timestamp 入群时间
        # message.from_group.name 事件群名
        # message.operate_qq.nickname 审批者QQ昵称
        # message.from_qq.nickname 入群者QQ昵称
        # 注意！触发此事件的同时可能会触发某人被邀请入群事件
        pass

    elif message.msg.type == xlz.types.EventTypes.群事件_某人被邀请入群.value:
        # message.logon_qq 框架QQ
        # message.from_group.group 事件群号
        # message.operate_qq.qq 邀请者QQ
        # message.from_qq.qq 入群者QQ
        # message.msg.timestamp 入群时间
        # message.from_group.name 事件群名
        # message.operate_qq.nickname 邀请者QQ昵称
        # message.from_qq.nickname 入群者QQ昵称
        # message.msg.text   为:[二维码/链接分享邀请],或:[普通邀请]
        # 注意！此事件与某人加入了群事件互不影响，独立触发
        pass

    elif message.msg.type == xlz.types.EventTypes.群事件_我被邀请加入群.value:
        # message.logon_qq 框架QQ
        # message.from_group.group 被邀群号
        # message.operate_qq.qq 邀请者QQ
        # message.msg.seq  处理所需Seq
        # message.msg.timestamp 邀请时间
        # message.from_group.name 被邀群名称
        # message.operate_qq.nickname 邀请者QQ昵称
        # message.from_qq.nickname 本人昵称
        # message.from_qq.qq  邀请者QQ
        pass

    elif message.msg.type == xlz.types.EventTypes.群事件_某人申请加群.value:
        # message.logon_qq 框架QQ
        # message.from_group.group 被申群号
        # message.operate_qq.qq 邀请者QQ
        # message.msg.seq操作所需Seq
        # message.msg.timestamp 申请时间
        # message.from_group.name 被申群名称
        # message.operate_qq.nickname 邀请者QQ昵称
        # message.from_qq.nickname 进群者QQ昵称
        # message.from_qq.qq  进群者QQ
        # message.msg.text 为：验证消息 加上 加群来源,格式为：验证消息[加群来源:xxx],如果加群者QQ存在风险被腾讯过滤,那么将加上[该帐号存在风险，请谨慎操作]后缀,验证消息内的[、]将被转义
        pass

    elif message.msg.type == xlz.types.EventTypes.群事件_某人退出了群.value:
        # message.logon_qq 框架QQ
        # message.from_group.group 被退群号
        # message.msg.timestamp 退群时间
        # message.from_group.name 被退群名称
        # message.from_qq.nickname 退群者QQ昵称
        # message.from_qq.qq  退群者QQ
        pass

    elif message.msg.type == xlz.types.EventTypes.群事件_某人被踢出群.value:
        # message.logon_qq 框架QQ
        # message.from_group.group 少人群号
        # message.msg.timestamp 被踢时间
        # message.from_group.name 少人群名称
        # message.from_qq.nickname 被踢者QQ昵称
        # message.from_qq.qq  被踢者QQ
        # message.operate_qq.qq 踢人QQ
        # message.operate_qq.nickname 踢人QQ昵称
        pass

    elif message.msg.type == xlz.types.EventTypes.群事件_某人撤回事件.value:
        # message.logon_qq 框架QQ
        # message.from_group.group 被撤群号
        # message.operate_qq.qq 撤消QQ (对方本人或管理员)
        # message.from_qq.qq 被撤QQ
        # message.msg.seq消息Seq
        # message.msg.timestamp 消息发送时间
        # message.from_group.name 被撤群名称
        # message.operate_qq.nickname 撤消QQ昵称
        # message.msg.text 撤回内容
        pass

    elif message.msg.type == xlz.types.EventTypes.群事件_开启全员禁言.value:
        # message.logon_qq 框架QQ
        # message.from_group.group 启用群号
        # message.operate_qq.qq 开启人QQ
        # message.msg.timestamp  开启时间
        # message.from_group.name 启用群名称
        # message.operate_qq.nickname 开启人QQ昵称
        pass

    elif message.msg.type == xlz.types.EventTypes.群事件_关闭全员禁言.value:
        # message.logon_qq 框架QQ
        # message.from_group.group 关闭群号
        # message.operate_qq.qq 关闭人QQ
        # message.msg.timestamp  关闭时间
        # message.from_group.name 关闭群名称
        # message.operate_qq.nickname 关闭人QQ昵称
        pass

    elif message.msg.type == xlz.types.EventTypes.群事件_开启匿名聊天.value:
        # message.logon_qq 框架QQ
        # message.from_group.group 启用群号
        # message.operate_qq.qq 开启人QQ
        # message.msg.timestamp  开启时间
        # message.from_group.name 启用群名称
        # message.operate_qq.nickname 开启人QQ昵称
        pass

    elif message.msg.type == xlz.types.EventTypes.群事件_关闭匿名聊天.value:
        # message.logon_qq 框架QQ
        # message.from_group.group 关闭群号
        # message.operate_qq.qq 关闭人QQ
        # message.msg.timestamp  关闭时间
        # message.from_group.name 关闭群名称
        # message.operate_qq.nickname 关闭人QQ昵称
        pass

    elif message.msg.type == xlz.types.EventTypes.群事件_某人被取消管理.value:
        # message.logon_qq 框架QQ
        # message.from_group.group 发生群号
        # message.from_qq.qq  被取消者QQ
        # message.msg.timestamp  取消时间
        # message.from_group.name 发生群名
        # message.from_qq.nickname 被取消者QQ昵称
        pass

    elif message.msg.type == xlz.types.EventTypes.群事件_某人被赋予管理.value:
        # message.logon_qq 框架QQ
        # message.from_group.group 发生群号
        # message.from_qq.qq  被赋予者QQ
        # message.msg.timestamp  取消时间
        # message.from_group.name 发生群名
        # message.from_qq.nickname 被赋予者QQ昵称
        pass

    elif message.msg.type == xlz.types.EventTypes.群事件_开启坦白说.value:
        # message.logon_qq 框架QQ
        # message.from_group.group 发生群号
        # message.from_group.name 发生群名
        pass

    elif message.msg.type == xlz.types.EventTypes.群事件_关闭坦白说.value:
        # message.logon_qq 框架QQ
        # message.from_group.group 发生群号
        # message.from_group.name 发生群名
        pass

    elif message.msg.type == xlz.types.EventTypes.群事件_允许群临时会话.value:
        # message.logon_qq 框架QQ
        # message.from_group.group 发生群号
        # message.from_group.name 发生群名
        pass

    elif message.msg.type == xlz.types.EventTypes.群事件_禁止群临时会话.value:
        # message.logon_qq 框架QQ
        # message.from_group.group 发生群号
        # message.from_group.name 发生群名
        pass

    elif message.msg.type == xlz.types.EventTypes.群事件_允许发起新的群聊.value:
        # message.logon_qq 框架QQ
        # message.from_group.group 发生群号
        # message.from_group.name 发生群名
        pass

    elif message.msg.type == xlz.types.EventTypes.群事件_禁止发起新的群聊.value:
        # message.logon_qq 框架QQ
        # message.from_group.group 发生群号
        # message.from_group.name 发生群名
        pass

    elif message.msg.type == xlz.types.EventTypes.群事件_允许上传群文件.value:
        # message.logon_qq 框架QQ
        # message.from_group.group 发生群号
        # message.from_group.name 发生群名
        pass

    elif message.msg.type == xlz.types.EventTypes.群事件_禁止上传群文件.value:
        # message.logon_qq 框架QQ
        # message.from_group.group 发生群号
        # message.from_group.name 发生群名
        pass

    elif message.msg.type == xlz.types.EventTypes.群事件_允许上传相册.value:
        # message.logon_qq 框架QQ
        # message.from_group.group 发生群号
        # message.from_group.name 发生群名
        pass

    elif message.msg.type == xlz.types.EventTypes.群事件_禁止上传相册.value:
        # message.logon_qq 框架QQ
        # message.from_group.group 发生群号
        # message.from_group.name 发生群名
        pass

    elif message.msg.type == xlz.types.EventTypes.群事件_展示成员群头衔.value:
        # message.logon_qq 框架QQ
        # message.from_group.group 发生群号
        # message.from_group.name 发生群名
        pass

    elif message.msg.type == xlz.types.EventTypes.群事件_隐藏成员群头衔.value:
        # message.logon_qq 框架QQ
        # message.from_group.group 发生群号
        # message.from_group.name 发生群名
        pass

    elif message.msg.type == xlz.types.EventTypes.群事件_群名变更.value:
        # message.logon_qq 框架QQ
        # message.from_group.group 发生群号
        # message.from_group.name 新的群名
        # message.from_qq.qq 更名者QQ
        # message.from_qq.nickname 更名者QQ昵称
        pass

    elif message.msg.type == xlz.types.EventTypes.群事件_系统提示.value:
        # message.logon_qq 框架QQ
        # message.from_group.group 来源群号
        # message.from_group.name 来源群名
        # message.from_qq.qq 提示触发者QQ
        # message.from_qq.nickname 提示触发者QQ昵称
        # message.msg.text QQ系统提示数据
        pass

    elif message.msg.type == xlz.types.EventTypes.群事件_群头像事件.value:
        # 这个事件表示此群更换了群头像或者上传了群头像(但是没换成这个)
        # message.logon_qq 框架QQ
        # message.from_group.group 发生群号
        # message.from_group.name 发生群名
        # message.from_qq.qq 操作者QQ
        # message.from_qq.nickname 操作者QQ昵称
        pass

    elif message.msg.type == xlz.types.EventTypes.群事件_入场特效.value:
        # message.logon_qq 框架QQ
        # message.from_group.group 入场群号
        # message.from_group.name 入场群名
        # message.from_qq.qq 入场者QQ
        # message.from_qq.nickname 入场者QQ昵称
        # message.msg.timestamp 入场时间戳
        # message.msg.text 入场特效Id
        pass

    elif message.msg.type == xlz.types.EventTypes.群事件_修改群名片.value:
        # message.logon_qq 框架QQ
        # message.from_group.group 改名片者来源群号
        # message.from_group.name 改名片者来源群名
        # message.from_qq.qq 改名片者QQ
        # message.from_qq.nickname 改名片者新名片
        # message.operate_qq.qq 改名片者QQ
        # message.operate_qq.nickname 改名片者旧名片
        # message.msg.timestamp 改名片时间戳
        pass

    elif message.msg.type == xlz.types.EventTypes.群事件_群被转让.value:
        # message.logon_qq 框架QQ
        # message.from_group.group 被转让群的群号
        # message.from_group.name 被转让群的群名
        # message.from_qq.qq 新群主QQ
        # message.from_qq.nickname 新群主QQ昵称
        # message.operate_qq.qq 旧群主QQ
        # message.operate_qq.nickname 旧群主QQ昵称
        # message.msg.timestamp 转让时间戳
        pass

    elif message.msg.type == xlz.types.EventTypes.群事件_某人的加群申请被拒绝.value:
        # message.logon_qq 框架QQ
        # message.from_group.group 触发事件的群号
        # message.from_group.name 触发事件的群名
        # message.operate_qq.qq 拒绝者QQ
        # message.operate_qq.nickname 拒绝者QQ昵称
        # message.from_qq.qq 被拒绝者QQ
        # message.from_qq.nickname 被拒绝者QQ昵称
        # message.msg.seq申请加群事件seq
        # message.msg.timestamp 触发时间戳
        pass

    elif message.msg.type == xlz.types.EventTypes.讨论组事件_讨论组名变更.value:
        # message.logon_qq 框架QQ
        # message.from_group.group 发生讨论组号
        # message.from_group.name 新的讨论组名
        # message.from_qq.qq 更名者QQ
        # message.from_qq.nickname 更名者QQ昵称
        pass

    elif message.msg.type == xlz.types.EventTypes.讨论组事件_某人撤回事件.value:  # 讨论组当中，只能自己撤回自己的消息，所以不存在"撤回者"的说法
        # message.logon_qq 框架QQ
        # message.from_group.group 被撤讨论组号
        # message.from_qq.qq 被撤QQ
        # message.msg.seq消息Seq
        # message.msg.timestamp 消息发送时间
        # message.from_group.name 被撤讨论组名称
        # message.msg.text 撤回内容
        pass

    elif message.msg.type == xlz.types.EventTypes.讨论组事件_某人被邀请入群.value:  # 目前讨论组不能主动加，只能被邀请，所以只有被邀请加入的事件
        # message.logon_qq 框架QQ
        # message.from_group.group 事件讨论组号
        # message.operate_qq.qq 邀请者QQ
        # message.from_qq.qq 入讨论组者QQ
        # message.msg.timestamp 入讨论组时间
        # message.from_group.name 事件讨论组名
        # message.operate_qq.nickname 邀请者QQ昵称
        # message.from_qq.nickname 入讨论组者QQ昵称
        # message.msg.text   为:[普通邀请] (因为讨论组分享的二维码、链接什么的已经失效了)
        pass

    elif message.msg.type == xlz.types.EventTypes.讨论组事件_某人退出了群.value:
        # message.logon_qq 框架QQ
        # message.from_group.group 被退讨论组Id
        # message.msg.timestamp 退出时间
        # message.from_group.name 被退讨论组名称
        # message.from_qq.nickname 退出者QQ昵称
        # message.from_qq.qq  退出者QQ
        pass

    elif message.msg.type == xlz.types.EventTypes.讨论组事件_某人被踢出群.value:
        # message.logon_qq 框架QQ
        # message.from_group.group 少人讨论组Id
        # message.msg.timestamp 被踢时间
        # message.from_group.name 少人讨论组名称
        # message.from_qq.nickname 被踢者QQ昵称
        # message.from_qq.qq  被踢者QQ
        # message.operate_qq.qq 踢人QQ
        # message.operate_qq.nickname 踢人QQ昵称
        pass

    elif message.msg.type == xlz.types.EventTypes.空间事件_与我相关.value:
        # message.logon_qq 框架QQ
        # message.operate_qq.qq 触发者QQ
        # message.operate_qq.nickname 触发者QQ昵称
        # message.msg.text 事件内容(包括说说点赞、评论、留言等，这个是腾讯返回的，不怎么详细)
        pass

    elif message.msg.type == xlz.types.EventTypes.框架事件_登录成功.value:
        # message.logon_qq 登录成功的框架QQ
        # message.from_qq.qq 登录成功的框架QQ
        # message.from_qq.nickname 登录成功的框架QQ昵称
        # message.msg.timestamp 登录成功的时间戳
        pass

    elif message.msg.type == xlz.types.EventTypes.框架事件_登录失败.value:
        # message.logon_qq 登录失败的框架QQ
        # message.from_qq.qq 登录失败的框架QQ
        # message.from_qq.nickname 登录失败的框架QQ昵称
        # message.msg.timestamp 登录失败的时间戳
        # message.msg.text 登录失败信息,格式为：登录错误状态+换行符+登录错误信息
        pass

    elif message.msg.type == xlz.types.EventTypes.框架事件_即将重启更新自身.value:
        # message.msg.timestamp 现行时间戳
        # message.msg.text 新版本更新内容(Ver 版本号+换行符+更新内容)
        pass

    elif message.msg.type == xlz.types.EventTypes.登录事件_移动设备上线.value:  # 不包括本身登录(!!!!!!由于腾讯通知机制的问题，本事件会被同时触发多次!!!!!!!!)
        # message.logon_qq 移动设备上线的QQ
        # message.msg.text 移动设备上线信息(包含appid)
        pass

    elif message.msg.type == xlz.types.EventTypes.登录事件_移动设备下线.value:  # 不包括本身下线以及被顶(!!!!!!由于腾讯通知机制的问题，本事件会被同时触发多次!!!!!!!!)
        # message.logon_qq 移动设备下线的QQ
        # message.msg.text 移动设备下线信息(包含appid)
        pass

    elif message.msg.type == xlz.types.EventTypes.登录事件_电脑上线.value:  # (!!!!!!由于腾讯通知机制的问题，本事件会被同时触发多次!!!!!!!!)
        # message.logon_qq 电脑上线的QQ
        # message.msg.text 电脑上线信息(不含appid)
        pass

    elif message.msg.type == xlz.types.EventTypes.登录事件_电脑下线.value:  # 无具体信息(!!!!!!由于腾讯通知机制的问题，本事件会被同时触发多次!!!!!!!!)
        # message.logon_qq 电脑下线的QQ
        pass

    elif message.msg.type == xlz.types.EventTypes.登录事件_PCQQ登录验证请求.value:
        # message.logon_qq PCQQ请求登录验证的QQ
        # message.msg.text PCQQ登录验证请求原始数据包,为Protobuf格式
        pass
