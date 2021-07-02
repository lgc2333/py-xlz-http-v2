# coding=utf-8
"""数据类型"""
import enum

import py_xlz_http as xlz


def _get_msg_type(code):
    """根据值获取消息类型文本"""
    try:
        name = MessageTypes(code).name
    except ValueError:
        return f'未知消息({code})'
    return name


def _get_evt_type(code):
    """根据值获取事件类型文本"""
    try:
        name = EventTypes(code).name
    except ValueError:
        return f'未知事件({code})'
    return name


class PrivateMsg(object):
    """私聊消息数据"""
    __slots__ = (
        'from_qq', 'logon_qq', 'timestamp', 'from_group', 'msg', 'red_packet', 'file', 'msg_part', 'session_token')

    class __cls_from_qq(object):
        def __init__(self, j: dict):
            self.qq: int = j['qq']
            self.qq2: int = j['qq2']
            self.nickname: str = j['nickname']

    class __cls_timestamp(object):
        def __init__(self, j: dict):
            self.recv: int = j['recv']
            self.send: int = j['send']

    class __cls_from_group(object):
        def __init__(self, j: dict):
            self.group: int = j['group']

    class __cls_msg(object):
        def __init__(self, j: dict):
            self.req: int = j['req']
            self.seq: int = j['seq']
            self.type: int = j['type']
            self.subtype: int = j['subtype']
            self.subtype_temp: int = j['subtemptype']
            self.text: str = j['text']
            self.bubble_id: int = j['bubbleid']

    class __cls_hb(object):
        def __init__(self, j: dict):
            self.type: int = j['type']

    class __cls_file(object):
        def __init__(self, j: dict):
            self.id: str = j['id']
            self.md5: str = j['md5']
            self.name: str = j['name']
            self.size: int = j['size']

    class __cls_msg_part(object):
        def __init__(self, j: dict):
            self.seq: int = j['seq']
            self.count: int = j['count']
            self.flag: int = j['flag']

    def __init__(self, j: dict):
        if not j['type'] == 'privatemsg':
            raise ValueError('This json string is not a private message data')
        self.from_qq = self.__cls_from_qq(j['fromqq'])
        self.logon_qq: int = j['logonqq']
        self.timestamp = self.__cls_timestamp(j['timestamp'])
        self.from_group = self.__cls_from_group(j['fromgroup'])
        self.msg = self.__cls_msg(j['msg'])
        self.red_packet = self.__cls_hb(j['hb'])
        self.file = self.__cls_file(j['file'])
        self.msg_part = self.__cls_msg_part(j['msgpart'])
        self.session_token: str = j['sessiontoken']

    def __str__(self):
        gin = ''
        subtmp = _get_msg_type(self.msg.type)

        if self.from_group.group:
            gin = f'[{self.from_group.group}] -> '

        if not (subtmp == '好友消息' or subtmp.startswith('未知消息')):
            subtmp = f'{subtmp},{_get_msg_type(self.msg.subtype_temp)}'

        return (f'Bot{self.logon_qq} -> [{subtmp}]'
                f'{gin}[{xlz.utils.usc2_to_unicode(self.from_qq.nickname)}({self.from_qq.qq})]：'
                f'{xlz.utils.usc2_to_unicode(self.msg.text)}')

    __repr__ = __str__


class GroupMsg(object):
    """群聊消息数据"""
    __slots__ = (
        'logon_qq', 'from_qq', 'from_group', 'timestamp', 'msg', 'msg_part', 'reserved_arg1', 'logon_qq_anonymous_id')

    class __cls_from_qq(object):
        def __init__(self, j: dict):
            self.qq: int = j['qq']
            self.card: str = j['card']
            self.spec_title: str = j['spectitle']
            self.group_level: int = j['grouplevel']
            self.anonymous_name: str = j['anonymousname']
            self.anonymous_id: str = j['anonymousid']

    class __cls_from_group(object):
        def __init__(self, j: dict):
            self.group: int = j['group']
            self.name: str = j['name']

    class __cls_timestamp(object):
        def __init__(self, j: dict):
            self.recv: int = j['recv']
            self.send: int = j['send']

    class __cls_msg(object):
        def __init__(self, j: dict):
            self.subtype: int = j['subtype']
            self.req: int = j['req']
            self.random: int = j['random']
            self.text: str = j['msg']
            self.msg_to_reply: str = j['msgtoreply']
            self.bubble_id: int = j['bubbleid']
            self.pendant_id: int = j['pendantid']
            self.font_id: int = j['fontid']

    class __cls_msg_part(object):
        def __init__(self, j: dict):
            self.seq: int = j['seq']
            self.count: int = j['count']
            self.flag: int = j['flag']

    def __init__(self, j: dict):
        if not j['type'] == 'groupmsg':
            raise ValueError('This json string is not a group message data')
        self.logon_qq: int = j['logonqq']
        self.from_qq = self.__cls_from_qq(j['fromqq'])
        self.from_group = self.__cls_from_group(j['fromgroup'])
        self.timestamp = self.__cls_timestamp(j['timestamp'])
        self.msg = self.__cls_msg(j['msg'])
        self.msg_part = self.__cls_msg_part(j['msgpart'])
        self.reserved_arg1: str = j['reservedarg1']
        self.logon_qq_anonymous_id: int = j['logonqqanonymousid']

    def __str__(self):
        return (f'Bot{self.logon_qq} -> [{_get_msg_type(self.msg.subtype)}]'
                f'[{xlz.utils.usc2_to_unicode(self.from_group.name)}({self.from_group.group})] -> '
                f'[{xlz.utils.usc2_to_unicode(self.from_qq.card)}({self.from_qq.qq})]：'
                f'{xlz.utils.usc2_to_unicode(self.msg.text)}')

    __repr__ = __str__


class EventMsg(object):
    """私聊消息数据"""
    __slots__ = ('from_qq', 'operate_qq', 'logon_qq', 'from_group', 'msg', 'red_packet', 'file')

    class __cls_from_qq(object):
        def __init__(self, j: dict):
            self.qq: int = j['qq']
            self.nickname: str = j['nickname']

    class __cls_operate_qq(object):
        def __init__(self, j: dict):
            self.qq: int = j['qq']
            self.nickname: str = j['nickname']

    class __cls_from_group(object):
        def __init__(self, j: dict):
            self.group: int = j['group']
            self.name: str = j['name']

    class __cls_msg(object):
        def __init__(self, j: dict):
            self.seq: int = j['seq']
            self.timestamp: int = j['timestamp']
            self.type: int = j['type']
            self.subtype: int = j['subtype']
            self.text: str = j['text']

    def __init__(self, j: dict):
        if not j['type'] == 'eventmsg':
            raise ValueError('This json string is not a event message data')
        self.from_qq = self.__cls_from_qq(j['fromqq'])
        self.operate_qq = self.__cls_operate_qq(j['operateqq'])
        self.logon_qq: int = j['logonqq']
        self.from_group = self.__cls_from_group(j['fromgroup'])
        self.msg = self.__cls_msg(j['msg'])

    def __str__(self):
        gin = ''
        txt = ''
        fr = ''

        if self.from_group.group:
            gin = f'[{xlz.utils.usc2_to_unicode(self.from_group.name)}({self.from_group.group})]'

        if self.from_qq.qq:
            fr = f'{xlz.utils.usc2_to_unicode(self.from_qq.nickname)}({self.from_qq.qq})'

        if self.operate_qq.qq:
            fr = f' -> [{xlz.utils.usc2_to_unicode(self.operate_qq.nickname)}({self.operate_qq.qq}) -> {fr}]'
        else:
            fr = f'-> [{fr}]'

        if self.msg.text:
            txt = f'：{xlz.utils.usc2_to_unicode(self.msg.text)}'

        return f'Bot{self.logon_qq} -> [{_get_evt_type(self.msg.type)}]{gin}{fr}{txt}'

    __repr__ = __str__


class ScheduleWork(object):
    def __init__(self, j: dict):
        if not j['type'] == 'schedulework':
            raise ValueError('This json string is not a schedule work message data')
        self.arg = j['arg']

    def __str__(self):
        return f'[定时任务]{self.arg}'

    __repr__ = __str__


class MessageTypes(enum.Enum):
    """消息类型"""
    临时会话 = 141
    临时会话_群临时 = 0
    临时会话_讨论组临时 = 1
    临时会话_公众号 = 129
    临时会话_网页QQ咨询 = 201
    好友消息 = 166
    讨论组消息 = 83
    群消息 = 134


class EventTypes(enum.Enum):
    """事件消息类型"""
    群事件_我被邀请加入群 = 1
    群事件_某人加入了群 = 2
    群事件_某人申请加群 = 3
    群事件_群被解散 = 4
    群事件_某人退出了群 = 5
    群事件_某人被踢出群 = 6
    群事件_某人被禁言 = 7
    群事件_某人撤回事件 = 8
    群事件_某人被取消管理 = 9
    群事件_某人被赋予管理 = 10
    群事件_开启全员禁言 = 11
    群事件_关闭全员禁言 = 12
    群事件_开启匿名聊天 = 13
    群事件_关闭匿名聊天 = 14
    群事件_开启坦白说 = 15
    群事件_关闭坦白说 = 16
    群事件_允许群临时会话 = 17
    群事件_禁止群临时会话 = 18
    群事件_允许发起新的群聊 = 19
    群事件_禁止发起新的群聊 = 20
    群事件_允许上传群文件 = 21
    群事件_禁止上传群文件 = 22
    群事件_允许上传相册 = 23
    群事件_禁止上传相册 = 24
    群事件_某人被邀请入群 = 25
    群事件_展示成员群头衔 = 26
    群事件_隐藏成员群头衔 = 27
    群事件_某人被解除禁言 = 28
    # 群事件_我被踢出 = 30  # 框架3.5.2已剔除
    群事件_群名变更 = 32
    群事件_系统提示 = 33
    群事件_群头像事件 = 34
    群事件_入场特效 = 35
    群事件_修改群名片 = 36
    群事件_群被转让 = 37
    群事件_匿名被禁言 = 40
    群事件_匿名被解除禁言 = 41
    群事件_某人的加群申请被拒绝 = 42
    空间事件_与我相关 = 29
    框架事件_登录成功 = 31
    框架事件_登录失败 = 38
    框架事件_即将重启更新自身 = 39
    讨论组事件_讨论组名变更 = 300
    讨论组事件_某人撤回事件 = 301
    讨论组事件_某人被邀请入群 = 302
    讨论组事件_某人退出了群 = 303
    讨论组事件_某人被踢出群 = 304
    好友事件_被好友删除 = 100
    好友事件_签名变更 = 101
    好友事件_昵称改变 = 102
    好友事件_某人撤回事件 = 103
    好友事件_有新好友 = 104
    好友事件_好友请求 = 105
    好友事件_对方同意了您的好友请求 = 106
    好友事件_对方拒绝了您的好友请求 = 107
    好友事件_资料卡点赞 = 108
    好友事件_签名点赞 = 109
    好友事件_签名回复 = 110
    好友事件_个性标签点赞 = 111
    好友事件_随心贴回复 = 112
    好友事件_随心贴增添 = 113
    好友事件_系统提示 = 114
    好友事件_随心贴点赞 = 115
    好友事件_匿名提问_被提问 = 116
    好友事件_匿名提问_被点赞 = 117
    好友事件_匿名提问_被回复 = 118
    好友事件_输入状态 = 119
    登录事件_电脑上线 = 200
    登录事件_电脑下线 = 201
    登录事件_移动设备上线 = 202
    登录事件_移动设备下线 = 203
    登录事件_PCQQ登录验证请求 = 204


class ApiRequestFailedException(Exception):
    def __init__(self, msg):
        super(ApiRequestFailedException, self).__init__(msg)


class ApiInitException(Exception):
    def __init__(self, msg):
        super(ApiInitException, self).__init__(msg)
