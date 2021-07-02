# coding=utf-8
"""
小栗子API

我一个人开发此项目难免有些疏漏，所以请积极发issue、提交pull request哦！感谢大家帮助完善这个项目！
"""
import hashlib
import inspect
import os
import random
import time
import traceback
import typing

import requests

import py_xlz_http as xlz

_inited = False
_url = ''
_user = ''
_password = ''
_proxies = {}
_timeout = 15

_session = requests.Session()


def _get_stack() -> str:
    """获取执行堆栈并格式化"""
    stack = []
    stacks = inspect.stack()
    stacks.reverse()
    for i in stacks[:-1]:
        stack.append(f'{i.filename[i.filename.rfind(os.sep) + 1:]}:{i.lineno}')
    return ' → '.join(stack)


def _md5_encode(string: str):
    """字符串md5加密"""
    if string:
        m = hashlib.md5()
        m.update(string.encode('utf-8'))
        return m.hexdigest()
    return ''


def _make_request(method, data: typing.Union[dict, bytes, None] = None, params: typing.Optional[dict] = None,
                  ignore_errors=False):
    """
    请求api

    :param method: 路径名，不带/
    :param data: 提交数据dict
    :param ignore_errors: 忽略访问时出错，返回None
    :return: ret
    """
    if not _inited:
        raise xlz.types.ApiInitException('API did not init yet')

    headers = {}
    if _user:
        # 设置了user，置请求头
        timestamp = int(time.time())  # 10位时间戳
        # #signature:md5(用户名+请求路径+md5(密码)+timestamp)
        signature = _md5_encode(f'{_user}/{method}{_md5_encode(_password)}{timestamp}')
        # 1.1.0.4及以后的版本支持请求头传递参数,user对应H-Auth-User,signature对应H-Auth-Signature,timestamp对应H-Auth-Timestamp
        headers['H-Auth-User'] = _user
        headers['H-Auth-Signature'] = signature
        headers['H-Auth-Timestamp'] = str(timestamp)

    t = int(round(time.time() * 1000))  # 13位时间戳，计算访问用时

    try:
        ret = _session.post(_url + method, data=data, params=params, headers=headers, proxies=_proxies,
                            timeout=_timeout)
        if data is None:
            data = {}
    except:
        if not ignore_errors:  # 不忽略错误
            xlz.logger.error(f'[{_get_stack()}]访问API {method} 失败\n{traceback.format_exc()}')
            raise xlz.types.ApiRequestFailedException(f'Request API {method} Failed')

        # 忽略错误
        xlz.logger.info(f'[{_get_stack()}]访问API {method} {data} [{int(round(time.time() * 1000)) - t}ms] -> None')
        return None
    else:
        spent_time = int(round(time.time() * 1000)) - t
        try:
            j = ret.json()
        except:
            if not ignore_errors:
                xlz.logger.error(
                    f'[{_get_stack()}]解析API {method} 返回json失败 [{spent_time}ms] -> {ret.text}\n'
                    f'{traceback.format_exc()}'
                )
                raise xlz.types.ApiRequestFailedException(f'Parse API {method}\'s return Failed (Raw text: {ret.text})')

            # 忽略错误
            xlz.logger.info(f'[{_get_stack()}]访问API {method} {data} [{spent_time}ms] -> {ret.content}')
            return ret.content
        else:
            xlz.logger.info(f'[{_get_stack()}]访问API {method} {data} [{spent_time}ms] -> {ret.text}')
            if j['err']:
                raise xlz.types.ApiRequestFailedException(j['err'])
            return j['ret']


def init(url: str = 'http://localhost:10429/', user: typing.Optional[str] = None,
         password: typing.Optional[str] = None, proxies: dict = None, timeout: int = 15):
    """
    置api访问数据

    :param url: api地址
    :param user: 用户名
    :param password: 密码
    :param timeout: 访问超时，单位秒
    :param proxies: 代理
    """
    global _url, _user, _password, _proxies, _timeout, _inited
    if _inited:
        raise xlz.types.ApiInitException('Can not init again')

    if user:
        if not password:
            password = ''
        _user = user
        _password = password

    _url = url if url.endswith('/') else url + '/'

    if proxies:
        _proxies = proxies

    _timeout = timeout

    _inited = True
    xlz.logger.info(f'置API访问数据 -> url={url} user={user} password={password} proxies={proxies} timeout={timeout}')


def is_inited() -> bool:
    """api是否置访问数据过"""
    return _inited  # 供外部调用


# 以下为API
# 我一个人开发此项目难免有些疏漏，所以请积极发issue、提交pull request哦！感谢大家帮助完善这个项目！
def add_log(log, text_clr=32768, bg_clr=16777215):
    """
    输出日志

    :param log: 日志文本
    :param text_clr: 文字颜色 可使用utils的颜色值转换函数获得 默认#008000
    :param bg_clr: 背景颜色 可使用utils的颜色值转换函数获得 默认#ffffff
    :return:
    """
    data = {'log': log, 'textclr': text_clr, 'bgclr': bg_clr}
    return _make_request('addlog', data)


def send_private_msg(logon_qq, to_qq, msg, msg_type=''):
    """
    发送好友消息

    :param msg_type: 类型(xml/json/留空)
    :param logon_qq: 框架QQ
    :param to_qq: 对方QQ
    :param msg: 消息文本
    :return:
    """
    data = {'type': msg_type, 'logonqq': logon_qq, 'toqq': to_qq, 'msg': msg}
    return _make_request('sendprivatemsg', data)


def send_group_msg(logon_qq, group, msg, msg_type='', anonymous=False):
    """
    发送群消息

    :param msg_type: 类型(xml/json/留空)
    :param logon_qq: 框架QQ
    :param group: 群号
    :param msg: 消息文本
    :param anonymous: 是否匿名(true,false)
    :return:
    """
    data = {'type': msg_type, 'logonqq': logon_qq, 'group': group, 'msg': msg, 'anonymous': str(anonymous).lower()}
    return _make_request('sendgroupmsg', data)


def send_group_temp_msg(logon_qq, group, to_qq, msg):
    """
    发送群临时消息

    :param logon_qq: 框架QQ
    :param group: 群号
    :param to_qq: 对方QQ
    :param msg: 消息文本
    :return:
    """
    data = {'logonqq': logon_qq, 'group': group, 'toqq': to_qq, 'msg': msg}
    return _make_request('sendgrouptempmsg', data)


def send_discussion_msg(logon_qq, discussion_id, msg, msg_type=''):
    """
    发送讨论组消息

    :param msg_type: 类型(xml/json/留空)
    :param logon_qq: 框架QQ
    :param discussion_id: 讨论组ID
    :param msg: 消息文本
    :return:
    """
    data = {'type': msg_type, 'logonqq': logon_qq, 'discussionid': discussion_id, 'msg': msg}
    return _make_request('senddiscussionmsg', data)


def send_discussion_temp_msg(logon_qq, discussion_id, to_qq, msg):
    """
    发送讨论组临时消息

    :param logon_qq: 框架QQ
    :param discussion_id: 讨论组ID
    :param to_qq: 对方QQ
    :param msg: 消息文本
    :return:
    """
    data = {'logonqq': logon_qq, 'discussionid': discussion_id, 'toqq': to_qq, 'msg': msg}
    return _make_request('senddiscussiontempmsg', data)


def add_friend(logon_qq, to_qq, msg, remark=''):
    """
    添加好友

    :param logon_qq: 框架QQ
    :param to_qq: 对方QQ
    :param msg: 验证消息文本
    :param remark: 备注
    :return:
    """
    data = {'logonqq': logon_qq, 'toqq': to_qq, 'msg': msg, 'remark': remark}
    return _make_request('addfriend', data)


def add_group(logon_qq, group, msg):
    """
    添加群

    :param logon_qq: 框架QQ
    :param group: 群号
    :param msg: 验证消息文本
    :return:
    """
    data = {'logonqq': logon_qq, 'group': group, 'msg': msg}
    return _make_request('addgroup', data)


def delete_friend(logon_qq, to_qq):
    """
    删除好友

    :param logon_qq: 框架QQ
    :param to_qq: 对方QQ
    :return:
    """
    data = {'logonqq': logon_qq, 'toqq': to_qq}
    return _make_request('deletefriend', data)


def block_friend(logon_qq, to_qq, is_block=True):
    """
    置屏蔽好友

    :param logon_qq: 框架QQ
    :param to_qq: 对方QQ
    :param is_block: 是否屏蔽(true,false)
    :return:
    """
    data = {'logonqq': logon_qq, 'toqq': to_qq, 'isblock': str(is_block).lower()}
    return _make_request('blockfriend', data)


def special_care_friend(logon_qq, to_qq, is_care=True):
    """
    置特别关心好友

    :param logon_qq: 框架QQ
    :param to_qq: 对方QQ
    :param is_care: 是否特别关心(true,false)
    :return:
    """
    data = {'logonqq': logon_qq, 'toqq': to_qq, 'iscare': str(is_care).lower()}
    return _make_request('speccarefriend', data)


def upload_friend_pic(logon_qq, to_qq, pic, path_type='', is_flash=False, is_gif=False, width=None, height=None):
    """
    上传好友图片

    :param logon_qq: 框架QQ
    :param to_qq: 对方QQ
    :param is_flash: 是否闪照(true,false)
    :param path_type: pic参数类型(path:本地路径,url:网络路径,usermem:共享内存id,其他或留空:BASE64编码数据(不推荐))
    :param pic: 图片(类型由type参数决定)
    :param width: 宽度
    :param height: 高度
    :param is_gif: 是否动图(true,false)
    :return:
    """
    data = {'logonqq': logon_qq, 'toqq': to_qq, 'isflash': str(is_flash).lower(), 'type': path_type, 'pic': pic,
            'width': width, 'height': height, 'isgif': str(is_gif).lower()}
    return _make_request('uploadfriendpic', data)


def upload_group_pic(logon_qq, group, pic, path_type='', is_flash=False, is_gif=False, width=None, height=None):
    """
    上传群图片

    :param logon_qq: 框架QQ
    :param group: 群号
    :param is_flash: 是否闪照(true,false)
    :param path_type: pic参数类型(path:本地路径,url:网络路径,usermem:共享内存id,其他或留空:BASE64编码数据(不推荐))
    :param pic: 图片(类型由type参数决定)
    :param width: 宽度
    :param height: 高度
    :param is_gif: 是否动图(true,false)
    :return:
    """
    data = {'logonqq': logon_qq, 'group': group, 'isflash': str(is_flash).lower(), 'type': path_type, 'pic': pic,
            'width': width, 'height': height, 'isgif': str(is_gif).lower()}
    return _make_request('uploadgrouppic', data)


def upload_friend_audio(logon_qq, to_qq, audio, audio_type=0, text='', path_type='', audio_time=None):
    """
    上传好友语音

    :param logon_qq: 框架QQ
    :param to_qq: 对方QQ
    :param audio_type: 语音类型(0普通语音,1变声语音,2文字语音,3红包匹配语音)
    :param text: 语音文字(文字语音填附加文字(腾讯貌似会自动替换为语音对应的文本),匹配语音填a、b、s、ss、sss，注意是小写)
    :param path_type: audio参数类型(path:本地路径,url:网络路径,usermem:共享内存id,其他或留空:BASE64编码数据(不推荐))
    :param audio: 语音(类型由type参数决定)
    :param audio_time: 时长
    :return:
    """
    data = {'logonqq': logon_qq, 'toqq': to_qq, 'audiotype': audio_type, 'text': text, 'type': path_type,
            'audio': audio, 'time': audio_time}
    return _make_request('uploadfriendaudio', data)


def upload_group_audio(logon_qq, group, audio, audio_type=0, text='', path_type='', audio_time=None):
    """
    上传群语音

    :param logon_qq: 框架QQ
    :param group: 群号
    :param audio_type: 语音类型(0普通语音,1变声语音,2文字语音,3红包匹配语音)
    :param text: 语音文字(文字语音填附加文字(腾讯貌似会自动替换为语音对应的文本),匹配语音填a、b、s、ss、sss，注意是小写)
    :param path_type: audio参数类型(path:本地路径,url:网络路径,usermem:共享内存id,其他或留空:BASE64编码数据(不推荐))
    :param audio: 语音(类型由type参数决定)
    :param audio_time: 时长
    :return:
    """
    data = {'logonqq': logon_qq, 'group': group, 'audiotype': audio_type, 'text': text, 'type': path_type,
            'audio': audio, 'time': audio_time}
    return _make_request('uploadgroupaudio', data)


def upload_face_pic(logon_qq, pic, path_type=''):
    """
    上传头像

    :param logon_qq: 框架QQ
    :param path_type: pic参数类型(path:本地路径,url:网络路径,usermem:共享内存id,其他或留空:BASE64编码数据(不推荐))
    :param pic: 图片(类型由type参数决定)
    :return:
    """
    data = {'logonqq': logon_qq, 'type': path_type, 'pic': pic}
    return _make_request('uploadfacepic', data)


def set_group_card(logon_qq, group, to_qq, new_card):
    """
    设置群名片

    :param logon_qq: 框架QQ
    :param group: 群号
    :param to_qq: 对方QQ
    :param new_card: 新名片
    :return:
    """
    data = {'logonqq': logon_qq, 'group': group, 'toqq': to_qq, 'newcard': new_card}
    return _make_request('setgroupcard', data)


def get_nickname(to_qq, logon_qq=None, from_cache=True):
    """
    取昵称

    :param logon_qq: (强制取昵称时需要)框架QQ
    :param to_qq: 对方QQ
    :param from_cache: 是否从缓存取(true,false)
    :return:
    """
    data = {'logonqq': logon_qq, 'toqq': to_qq, 'fromcache': str(from_cache).lower()}
    return _make_request('getnickname', data)


def get_skey(logon_qq):
    """
    获取skey

    :param logon_qq: 框架QQ
    :return:
    """
    data = {'logonqq': logon_qq}
    return _make_request('getskey', data)


def get_p_skey(logon_qq, domain):
    """
    获取p_skey

    :param logon_qq: 框架QQ
    :param domain: 域
    :return:
    """
    data = {'logonqq': logon_qq, 'domain': domain}
    return _make_request('getpskey', data)


def get_client_key(logon_qq):
    """
    获取client_key

    :param logon_qq: 框架QQ
    :return:
    """
    data = {'logonqq': logon_qq}
    return _make_request('getclientkey', data)


def get_logon_qq():
    """
    取框架QQ

    :return:
    """
    return _make_request('getlogonqq')


def get_friend_list(logon_qq):
    """
    取好友列表

    :param logon_qq: 框架QQ
    :return:
    """
    data = {'logonqq': logon_qq}
    return _make_request('getfriendlist', data)


def get_group_list(logon_qq):
    """
    取群列表

    :param logon_qq: 框架QQ
    :return:
    """
    data = {'logonqq': logon_qq}
    return _make_request('getgrouplist', data)


def get_group_member_list(logon_qq, group):
    """
    取群成员列表

    :param logon_qq: 框架QQ
    :param group: 群号
    :return:
    """
    data = {'logonqq': logon_qq, 'group': group}
    return _make_request('getgroupmemberlist', data)


def set_group_admin(logon_qq, group, to_qq, un_admin=False):
    """
    设置管理员

    :param logon_qq: 框架QQ
    :param group: 群号
    :param to_qq: 对方QQ
    :param un_admin: 取消管理员(true,false)
    :return:
    """
    data = {'logonqq': logon_qq, 'group': group, 'toqq': to_qq, 'unadmin': str(un_admin).lower()}
    return _make_request('setgroupadmin', data)


def get_group_admin_list(logon_qq, group):
    """
    取群管理层列表

    :param logon_qq: 框架QQ
    :param group: 群号
    :return:
    """
    data = {'logonqq': logon_qq, 'group': group}
    return _make_request('getgroupadminlist', data)


def get_group_card(logon_qq, group, to_qq):
    """
    取群名片

    :param logon_qq: 框架QQ
    :param group: 群号
    :param to_qq: 对方QQ
    :return:
    """
    data = {'logonqq': logon_qq, 'group': group, 'toqq': to_qq}
    return _make_request('getgroupcard', data)


def get_signature(logon_qq, to_qq):
    """
    取个性签名

    :param logon_qq: 框架QQ
    :param to_qq: 对方QQ
    :return:
    """
    data = {'logonqq': logon_qq, 'toqq': to_qq}
    return _make_request('getsignat', data)


def set_nickname(logon_qq, nickname):
    """
    修改昵称

    :param logon_qq: 框架QQ
    :param nickname: 新昵称
    :return:
    """
    data = {'logonqq': logon_qq, 'nickname': nickname}
    return _make_request('setnickname', data)


def set_signature(logon_qq, signature, pos=None):
    """
    修改个性签名

    :param logon_qq: 框架QQ
    :param signature: 签名
    :param pos: 签名地点
    :return:
    """
    data = {'logonqq': logon_qq, 'signat': signature, 'pos': pos}
    return _make_request('setsignat', data)


def kick_group_member(logon_qq, group, to_qq, refuse_add_request=False):
    """
    删除群成员

    :param logon_qq: 框架QQ
    :param group: 群号
    :param to_qq: 对方QQ(批量用|分割)
    :param refuse_add_request: 拒绝加群申请(true,false)
    :return:
    """
    data = {'logonqq': logon_qq, 'group': group, 'toqq': to_qq, 'ignoreaddgrequest': str(refuse_add_request).lower()}
    return _make_request('kickgroupmember', data)


def mute_group_member(logon_qq, group, to_qq, mute_time=0):
    """
    禁言群成员

    :param logon_qq: 框架QQ
    :param group: 群号
    :param to_qq: 对方QQ
    :param mute_time: 禁言时长，为0解禁
    :return:
    """
    data = {'logonqq': logon_qq, 'group': group, 'toqq': to_qq, 'time': mute_time}
    return _make_request('mutegroupmember', data)


def exit_group(logon_qq, group, dismiss=False):
    """
    退群

    :param logon_qq: 框架QQ
    :param group: 群号
    :param dismiss: 是否解散群(true,false)
    :return:
    """
    data = {'logonqq': logon_qq, 'group': group, 'dismiss': str(dismiss).lower()}
    return _make_request('exitgroup', data)


def upload_group_face_pic(logon_qq, group, pic, path_type=''):
    """
    上传群头像

    :param logon_qq: 框架QQ
    :param group: 群号
    :param path_type: pic参数类型(path:本地路径,url:网络路径,usermem:共享内存id,其他或留空:BASE64编码数据(不推荐))
    :param pic: 图片(类型由type参数决定)
    :return:
    """
    data = {'logonqq': logon_qq, 'group': group, 'type': path_type, 'pic': pic}
    return _make_request('uploadgroupfacepic', data)


def mute_group(logon_qq, group, is_mute=True):
    """
    全员禁言

    :param logon_qq: 框架QQ
    :param group: 群号
    :param is_mute: 是否禁言
    :return:
    """
    data = {'logonqq': logon_qq, 'group': group, 'ismute': str(is_mute).lower()}
    return _make_request('mutegroup', data)


def set_group_privilege_1(p_type, is_allow=False):
    """
    设置群权限

    :param p_type: 类型(newgroup:发起新的群聊,newtempsession:发起临时会话,uploadfile:上传文件,uploadimage:上传图片,invitefriend:邀请好友加群,anonymouschat:匿名聊天,tanbaishuo:坦白说,viewhistmsg:新成员查看历史消息)
    :param is_allow: 是否允许(true,false)
    :return:
    """
    data = {'type': p_type, 'isallow': str(is_allow).lower()}
    return _make_request('setgrouppriv', data)


def set_group_privilege_2(p_type, value):
    """
    设置群权限

    :param p_type: 类型(setinviteway:邀请方式设置,limitmsgspd:限制发言频率,setnicknamerule:设置群昵称规则,setsearchway:设置群查找方式)
    :param value: 值[(setintiveway:1.无需审核;2.需要管理员审核;3.100人以内无需审核)(limitmsgspd:限制每分钟多少条发言,为0表示无限制)(setnicknamerule:对于易语言不支持的utf8字符,需usc2编码)(setsearchway:0不允许,1通过群号或关键词,2仅可通过群号,默认1)]
    :return:
    """
    data = {'type': p_type, 'value': value}
    return _make_request('setgrouppriv', data)


def delete_msg(msg_type, logon_qq, msg_random, msg_req, msg_time=None, to_qq=None, group=None, discussion_id=None):
    """
    撤回消息

    :param msg_type: 类型(private:私聊消息,group:群消息,discussion:讨论组消息)
    :param logon_qq: 框架QQ
    :param to_qq: 对方QQ(仅私聊聊消息需要)
    :param discussion_id: 讨论组id(仅讨论组消息需要)
    :param group: 群号(仅群消息需要)
    :param msg_random: 消息random
    :param msg_req: 消息req
    :param msg_time: 消息time(仅私聊消息需要)
    :return:
    """
    data = {'type': msg_type, 'logonqq': logon_qq, 'toqq': to_qq, 'discussionid': discussion_id, 'group': group,
            'random': msg_random, 'req': msg_req, 'time': msg_time}
    return _make_request('deletemsg', data)


def set_share_pos(logon_qq, group, long, lat, enable=True):
    """
    设置位置共享

    :param logon_qq: 框架QQ
    :param group: 群号
    :param long: 经度
    :param lat: 纬度
    :param enable: 是否开启(true,false)
    :return:
    """
    data = {'logonqq': logon_qq, 'group': group, 'long': long, 'lat': lat, 'enable': str(enable).lower()}
    return _make_request('setsharepos', data)


def upload_pos(logon_qq, group, long, lat):
    """
    上报当前位置

    :param logon_qq: 框架QQ
    :param group: 群号
    :param long: 经度
    :param lat: 纬度
    :return:
    """
    data = {'logonqq': logon_qq, 'group': group, 'long': long, 'lat': lat}
    return _make_request('uploadpos', data)


def get_mute_time(logon_qq, group):
    """
    取禁言时长

    :param logon_qq: 框架QQ
    :param group: 群号
    :return:
    """
    data = {'logonqq': logon_qq, 'group': group}
    return _make_request('getmutetime', data)


def set_group_add_request(logon_qq, group, from_qq, seq, event_type, op_type=11, reason='', is_risk=False):
    """
    处理群验证事件

    :param logon_qq: 框架QQ
    :param group: 群号
    :param from_qq: 来源QQ
    :param seq: 消息Seq
    :param op_type: 操作类型(11同意,12拒绝,14忽略)
    :param event_type: 事件类型(1:我被邀请加入群,3:某人申请加群)
    :param reason: 拒绝理由
    :param is_risk: 是否为风险号(true,false)
    :return:
    """
    data = {'logonqq': logon_qq, 'group': group, 'fromqq': from_qq, 'seq': seq, 'optype': op_type,
            'eventtype': event_type, 'reason': reason, 'isrisk': str(is_risk).lower()}
    return _make_request('setgroupaddrequest', data)


def set_friend_add_request(logon_qq, from_qq, seq, op_type=1):
    """
    处理好友验证事件

    :param logon_qq: 框架QQ
    :param from_qq: 来源QQ
    :param seq: 消息Seq
    :param op_type: 操作类型(1同意,2拒绝)
    :return:
    """
    data = {'logonqq': logon_qq, 'fromqq': from_qq, 'seq': seq, 'optype': op_type}
    return _make_request('setfriendaddrequest', data)


def get_forwarded_msg(logon_qq, res_id):
    """
    获取转发聊天记录内容

    :param logon_qq: 框架QQ
    :param res_id: resid
    :return:
    """
    data = {'logonqq': logon_qq, 'resid': res_id}
    return _make_request('getforwardedmsg', data)


def upload_group_file(logon_qq, group, local_path, remote_path):
    """
    上传群文件(无返回)

    :param logon_qq: 框架QQ
    :param group: 群号
    :param local_path: 本地文件路径
    :param remote_path: 群文件夹名
    """
    data = {'logonqq': logon_qq, 'group': group, 'localpath': local_path, 'remotepath': remote_path}
    return _make_request('uploadgroupfile', data, ignore_errors=True)


def create_group_folder(logon_qq, group, name):
    """
    创建群文件夹

    :param logon_qq: 框架QQ
    :param group: 群号
    :param name: 文件夹名
    :return:
    """
    data = {'logonqq': logon_qq, 'group': group, 'name': name}
    return _make_request('creategroupfolder', data)


def rename_group_folder(logon_qq, group, old_name, new_name):
    """
    重命名群文件夹

    :param logon_qq: 框架QQ
    :param group: 群号
    :param old_name: 旧文件夹名
    :param new_name: 新文件夹名
    :return:
    """
    data = {'logonqq': logon_qq, 'group': group, 'oldname': old_name, 'newname': new_name}
    return _make_request('renamegroupfolder', data)


def delete_group_folder(logon_qq, group, name):
    """
    删除群文件夹

    :param logon_qq: 框架QQ
    :param group: 群号
    :param name: 文件夹名
    :return:
    """
    data = {'logonqq': logon_qq, 'group': group, 'name': name}
    return _make_request('deletegroupfolder', data)


def delete_group_file(logon_qq, group, fileid, folder=''):
    """
    删除群文件

    :param logon_qq: 框架QQ
    :param group: 群号
    :param fileid: 文件id
    :param folder: 文件夹名，根目录留空或填/
    :return:
    """
    data = {'logonqq': logon_qq, 'group': group, 'fileid': fileid, 'folder': folder}
    return _make_request('deletegroupfile', data)


def save_file_to_wei_yun(logon_qq, group, fileid):
    """
    保存文件到微云

    :param logon_qq: 框架QQ
    :param group: 群号
    :param fileid: 文件id
    :return:
    """
    data = {'logonqq': logon_qq, 'group': group, 'fileid': fileid}
    return _make_request('savefiletowydrive', data)


def move_group_file(logon_qq, group, fileid, folder, new_folder):
    """
    移动群文件

    :param logon_qq: 框架QQ
    :param group: 群号
    :param fileid: 文件id
    :param folder: 文件夹
    :param new_folder: 新文件夹
    :return:
    """
    data = {'logonqq': logon_qq, 'group': group, 'fileid': fileid, 'folder': folder, 'newfolder': new_folder}
    return _make_request('movegroupfile', data)


def get_group_file_list(logon_qq, group, folder=''):
    """
    取群文件列表

    :param logon_qq: 框架QQ
    :param group: 群号
    :param folder: 文件夹，根目录留空或填/
    :return:
    """
    data = {'logonqq': logon_qq, 'group': group, 'folder': folder}
    return _make_request('getgroupfilelist', data)


def set_online_state(logon_qq, main, sun=None, power=None):
    """
    设置在线状态

    :param logon_qq: 框架QQ
    :param main: 主状态(11在线,31离开,41隐身,50忙碌,60Q我吧,70请勿打扰)
    :param sun: 子状态(当main=11时，可进一步设置,0普通在线,1000我的电量,1011信号弱,1024在线学习,1025在家旅游,1027TiMi中,1016睡觉中,1017游戏中,1018学习中,1019吃饭中,1021煲剧中,1053汪汪汪,1032熬夜中,1050打球中,1051恋爱中,1052我没事,1028我在听歌,40001在地球,41042移动中,41033在小区,41034在学校,41035在公园,41036在海边,41037在机场,41038在商场,41039在咖啡厅,41041在餐厅,1022度假中,1020健身中,1056嗨到起飞,1058元气满满,1057美滋滋,1059悠哉哉,1060无聊中,1061想静静,1062我太难了,1063一言难尽,1064吃鸡中,1069遇见春天)
    :param power: 电量(sun=1000时，可以设置上报电量，取值1到100，如果想显示正在充电，取值为128+电量)
    :return:
    """
    data = {'logonqq': logon_qq, 'main': main, 'sun': sun, 'power': power}
    return _make_request('setonlinestate', data)


def send_like(logon_qq, to_qq):
    """
    QQ点赞

    :param logon_qq: 框架QQ
    :param to_qq: 对方QQ
    :return:
    """
    data = {'logonqq': logon_qq, 'toqq': to_qq}
    return _make_request('sendlike', data)


def get_photo_url(photo, logon_qq, group):
    """
    取图片下载地址

    :param photo: 图片代码
    :param logon_qq: 框架QQ
    :param group: 群号
    :return:
    """
    data = {'photo': photo, 'logonqq': logon_qq, 'group': group}
    return _make_request('getphotourl', data)


def query_friend_info(logon_qq, to_qq):
    """
    查询好友信息(也可查非好友,返回的json中vips.type:1SVIP 113QQ大会员 105微云会员 101红钻 102黄钻 103绿钻 104情侣黄钻 4腾讯视频VIP 107SVIP+腾讯视频 110SVIP+QQ音乐 108大王超级会员)

    :param logon_qq: 框架QQ
    :param to_qq: 对方QQ
    :return:
    """
    data = {'logonqq': logon_qq, 'toqq': to_qq}
    return _make_request('queryfriendinfo', data)


def query_group_info(logon_qq, group):
    """
    查询群信息

    :param logon_qq: 框架QQ
    :param group: 群号
    :return:
    """
    data = {'logonqq': logon_qq, 'group': group}
    return _make_request('querygroupinfo', data)


def forward_file_group_to_group(logon_qq, from_group, to_group, fileid):
    """
    转发文件(群文件转发至群)

    :param logon_qq: 框架QQ
    :param from_group: 来源群号
    :param to_group: 目标群号
    :param fileid: 文件ID
    :return:
    """
    data = {'type': 1, 'logonqq': logon_qq, 'fromgroup': from_group, 'togroup': to_group, 'fileid': fileid}
    return _make_request('forwardfile', data)


def forward_file_group_to_friend(logon_qq, from_group, to_qq, fileid, filename, file_size):
    """
    转发文件(群文件转发至好友)

    :param logon_qq: 框架QQ
    :param from_group: 来源群号
    :param to_qq: 目标QQ
    :param fileid: 文件ID
    :param filename: 文件名
    :param file_size: 文件大小
    :return:
    """
    data = {'type': 2, 'logonqq': logon_qq, 'fromgroup': from_group, 'toqq': to_qq, 'fileid': fileid,
            'filename': filename, 'filesize': file_size}
    return _make_request('forwardfile', data)


def forward_file_friend_to_friend(logon_qq, to_qq, fileid, filename, file_size):
    """
    转发文件(好友文件转发至好友)

    :param logon_qq: 框架QQ
    :param to_qq: 目标QQ
    :param fileid: 文件ID
    :param filename: 文件名
    :param file_size: 文件大小
    :return:
    """
    data = {'type': 3, 'logonqq': logon_qq, 'toqq': to_qq, 'fileid': fileid, 'filename': filename,
            'filesize': file_size}
    return _make_request('forwardfile', data)


def set_group_msg_receive(logon_qq, group, set_type=1):
    """
    置群消息接收

    :param logon_qq: 框架QQ
    :param group: 群号
    :param set_type: 设置类型(1接收并提醒,2收进群助手,3屏蔽群消息,4接收不提醒)
    :return:
    """
    data = {'logonqq': logon_qq, 'group': group, 'settype': set_type}
    return _make_request('setgroupmsgreceive', data)


def send_free_gift(logon_qq, group, to_qq, gift_id):
    """
    发送免费礼物

    :param logon_qq: 框架QQ
    :param group: 群号
    :param to_qq: 对方QQ
    :param gift_id: 礼物ID(367告白话筒;299卡布奇诺;302猫咪手表;280牵你的手;281可爱猫咪;284神秘面具;285甜wink;286我超忙的;289快乐肥宅水;290幸运手链;313坚强;307绒绒手套;312爱心口罩;308彩虹糖果)
    :return:
    """
    data = {'logonqq': logon_qq, 'group': group, 'toqq': to_qq, 'giftid': gift_id}
    return _make_request('sendfreegift', data)


def get_friend_online_state(logon_qq, to_qq):
    """
    取好友在线状态

    :param logon_qq: 框架QQ
    :param to_qq: 对方QQ
    :return:
    """
    data = {'logonqq': logon_qq, 'toqq': to_qq}
    return _make_request('getfriendonlinestate', data)


def get_qq_wallet_info(logon_qq):
    """
    取QQ钱包个人信息

    :param logon_qq: 框架QQ
    :return:
    """
    data = {'logonqq': logon_qq}
    return _make_request('getqqwalletinfo', data)


def get_order_info(logon_qq, order_num):
    """
    获取订单详情

    :param logon_qq: 框架QQ
    :param order_num: 订单号
    :return:
    """
    data = {'logonqq': logon_qq, 'ordernum': order_num}
    return _make_request('getorderinfo', data)


def submit_pay_verify_code(logon_qq, verify_code, pay_pwd, token_id, skey, bank_type, mobile, business_type,
                           pay_random, transaction_id, purchaser_id, token, auth_params):
    """
    提交支付验证码

    :param logon_qq: 框架QQ
    :param verify_code: 验证码
    :param pay_pwd: 支付密码
    :param token_id:
    :param skey:
    :param bank_type:
    :param mobile:
    :param business_type:
    :param pay_random: random
    :param transaction_id:
    :param purchaser_id:
    :param token:
    :param auth_params:
    :return:
    """
    data = {'logonqq': logon_qq, 'vfcode': verify_code, 'paypwd': pay_pwd, 'token_id': token_id, 'skey': skey,
            'bank_type': bank_type, 'mobile': mobile, 'business_type': business_type, 'random': pay_random,
            'transaction_id': transaction_id, 'purchaser_id': purchaser_id, 'token': token, 'auth_params': auth_params}
    return _make_request('submitpayvfcode', data)


def share_music(logon_qq, to, song_name, singer_name, jump_url, image_url, file_url, app_type=0, to_type=0):
    """
    分享音乐

    :param logon_qq: 框架QQ
    :param to: 对方
    :param song_name: 歌曲名
    :param singer_name: 歌手名
    :param jump_url: 跳转地址
    :param image_url: 封面地址
    :param file_url: 文件地址
    :param app_type: 应用类型(0QQ音乐,1虾米音乐,2酷我音乐,3酷狗音乐,4网易云音乐,默认0)
    :param to_type: 对方类型(0私聊,1群聊,2讨论组,默认0)
    :return:
    """
    data = {'logonqq': logon_qq, 'to': to, 'songname': song_name, 'singername': singer_name, 'jumpurl': jump_url,
            'imageurl': image_url, 'fileurl': file_url, 'apptype': app_type, 'totype': to_type}
    return _make_request('sharemusic', data)


def send_group_red_packet(packet_type, logon_qq, count, amount, group, text, pay_pwd, bankcard_id=0, skin_id=None,
                          to=None, is_avg=False):
    """
    发送群红包(银行卡支付时，若需要短信验证码，将返回验证码信息，使用API【提交支付验证码】进行验证处理)

    :param packet_type: 类型(norm:普通红包,lucky:拼手气红包,key:口令红包,draw:画图红包,audio:语音红包,jielong:接龙红包,exclusive:专属红包,rareword:生僻字红包)
    :param logon_qq: 框架QQ
    :param count: 总数量
    :param amount: 总金额
    :param group: 群号
    :param to: 领取人(仅专属红包可用)
    :param text: 文本或祝福语
    :param skin_id: 皮肤ID(1522光与夜之恋,1527代号:三国(打了一辈子仗),1525街霸:对决,1518代号:三国(俺送红包来了),1476天涯明月刀,1512一人之下。其他皮肤id自己找)(仅普通红包|拼手气红包可用)
    :param is_avg: 是否均分，不均分为拼手气(仅专属红包可用)
    :param pay_pwd: 支付密码
    :param bankcard_id: 银行卡序列(大于0时使用银行卡支付)
    :return:
    """
    data = {'type': packet_type, 'logonqq': logon_qq, 'count': count, 'amount': amount, 'group': group, 'to': to,
            'text': text, 'skinid': skin_id, 'isavg': str(is_avg).lower(), 'paypwd': pay_pwd, 'bankcardid': bankcard_id}
    return _make_request('sendgroupredpacket', data)


def send_friend_red_packet(packet_type, logon_qq, count, amount, to_qq, text, pay_pwd, bankcard_id=0, skin_id=None):
    """
    发送好友红包(银行卡支付时，若需要短信验证码，将返回验证码信息，使用API【提交支付验证码】进行验证处理)

    :param packet_type: 类型(norm:普通红包,key:口令红包,draw:画图红包,audio:语音红包,jielong:接龙红包,rareword:生僻字红包)
    :param logon_qq: 框架QQ
    :param count: 总数量
    :param amount: 总金额
    :param to_qq: 对方QQ
    :param text: 文本或祝福语
    :param skin_id: 皮肤ID(1522光与夜之恋,1527代号:三国(打了一辈子仗),1525街霸:对决,1518代号:三国(俺送红包来了),1476天涯明月刀,1512一人之下。其他皮肤id自己找)(仅普通红包可用)
    :param pay_pwd: 支付密码
    :param bankcard_id: 银行卡序列(大于0时使用银行卡支付)
    :return:
    """
    data = {'type': packet_type, 'logonqq': logon_qq, 'count': count, 'amount': amount, 'toqq': to_qq, 'text': text,
            'skinid': skin_id, 'paypwd': pay_pwd, 'bankcardid': bankcard_id}
    return _make_request('sendfriendredpacket', data)


def set_special_title(logon_qq, group, to_qq, special_title=''):
    """
    设置专属头衔

    :param logon_qq: 框架QQ
    :param group: 群号
    :param to_qq: 对方QQ
    :param special_title: 头衔
    :return:
    """
    data = {'logonqq': logon_qq, 'group': group, 'toqq': to_qq, 'spectitle': special_title}
    return _make_request('setspectitle', data)


def login_qq(logon_qq):
    """
    登录指定QQ

    :param logon_qq: 框架QQ
    :return:
    """
    data = {'logonqq': logon_qq}
    return _make_request('loginqq', data)


def logout_qq(logon_qq):
    """
    下线指定QQ

    :param logon_qq: 框架QQ
    :return:
    """
    data = {'logonqq': logon_qq}
    return _make_request('logoutqq', data)


def get_group_not_recv_red_packet_list(logon_qq, group):
    """
    取群未领红包列表

    :param logon_qq: 框架QQ
    :param group: 群号
    :return:
    """
    data = {'logonqq': logon_qq, 'group': group}
    return _make_request('getnoreredpacketlist', data)


def set_input_state(logon_qq, to_qq, state=1):
    """
    设置输入状态

    :param logon_qq: 框架QQ
    :param to_qq: 对方QQ
    :param state: 输入状态(1:正在输入,2:关闭显示,3:正在说话)
    :return:
    """
    data = {'logonqq': logon_qq, 'toqq': to_qq, 'state': state}
    return _make_request('setinputstate', data)


def modify_profile(logon_qq, nickname=None, sex=1, birthday=None, occupation=1, company=None, location=None,
                   hometown=None, email=None,
                   description=None):
    """
    修改资料

    :param logon_qq: 框架QQ
    :param nickname: 昵称
    :param sex: 性别(1:男,2:女,默认男)
    :param birthday: 生日(格式：2020/5/5,均为整数)
    :param occupation: 职业(1:IT,2:制造,3:医疗,4:金融,5:商业,6:文化,7:艺术,8:法律,9:教育,10:行政,11:模特,12:空姐,13:学生,14:其他职业，默认1)
    :param company: 公司名
    :param location: 所在地(国家代码|省份代码|市代码|区字母|区代码，如：49|13110|56|NK|51，表示中国江西省吉安市青原区，这些数据是腾讯的数据，非国际数据)
    :param hometown: 家乡(国家代码|省份代码|市代码|区字母|区代码，如：49|13110|56|NI|50，表示中国江西省吉安市吉州区，这些数据是腾讯的数据，非国际数据)
    :param email: 邮箱
    :param description: 个人说明
    :return:
    """
    data = {'logonqq': logon_qq, 'nickname': nickname, 'sex': sex, 'birthday': birthday, 'occupaction': occupation,
            'company': company, 'location': location, 'hometown': hometown, 'email': email, 'description': description}
    return _make_request('modifyprofile', data)


def get_file_url(chat_type, logon_qq, fileid, filename, group=None, discussion_id=None):
    """
    取文件下载地址

    :param chat_type: 类型(group:群,friend:好友,discussion:讨论组)
    :param logon_qq: 框架QQ
    :param group: 群号(群文件可用)
    :param discussion_id: 讨论组ID(讨论组文件可用)
    :param fileid: 文件ID
    :param filename: 文件名
    :return:
    """
    data = {'type': chat_type, 'logonqq': logon_qq, 'group': group, 'discussionid': discussion_id, 'fileid': fileid,
            'filename': filename}
    return _make_request('getfileurl', data)


def call_friend(logon_qq, to_qq):
    """
    打好友电话

    :param logon_qq: 框架QQ
    :param to_qq: 对方QQ
    :return:
    """
    data = {'logonqq': logon_qq, 'toqq': to_qq}
    return _make_request('callfriend', data)


def double_click_avatar(chat_type, logon_qq, to_qq, group=None):
    """
    头像双击

    :param chat_type: 类型(friend:私聊,group:群聊)
    :param logon_qq: 框架QQ
    :param to_qq: 对方QQ
    :param group: 群号(群聊可用)
    :return:
    """
    data = {'type': chat_type, 'logonqq': logon_qq, 'toqq': to_qq, 'group': group}
    return _make_request('doubleclickavator', data)


def get_group_preview(logon_qq, group):
    """
    取群成员简略信息

    :param logon_qq: 框架QQ
    :param group: 群号
    :return:
    """
    data = {'logonqq': logon_qq, 'group': group}
    return _make_request('getgrouppreview', data)


def pin_chat(chat_type, logon_qq, qq=None, group=None, is_top=True):
    """
    消息置顶

    :param chat_type: 类型(qq:私聊,group:群聊)
    :param logon_qq: 框架QQ
    :param qq: 对方QQ(私聊可用)
    :param group: 群号(群聊可用)
    :param is_top: 是否置顶(true,false)
    :return:
    """
    data = {'type': chat_type, 'logonqq': logon_qq, 'qq': qq, 'group': group, 'istop': str(is_top).lower()}
    return _make_request('setmsgtop', data)


def get_add_group_url(logon_qq, group):
    """
    取加群链接

    :param logon_qq: 框架QQ
    :param group: 群号
    :return:
    """
    data = {'logonqq': logon_qq, 'group': group}
    return _make_request('getaddgurl', data)


def set_essence_msg(logon_qq, group, req, msg_random, is_essence=True):
    """
    设置精华消息

    :param logon_qq: 框架QQ
    :param group: 群号
    :param req: 消息req
    :param msg_random: 消息random
    :param is_essence: 是否精华(true,false)
    :return:
    """
    data = {'logonqq': logon_qq, 'group': group, 'req': req, 'random': msg_random, 'isessence': str(is_essence).lower()}
    return _make_request('setessencemsg', data)


def invite_friend_to_group(logon_qq, to_group, from_group, qq):
    """
    邀请好友加群

    :param logon_qq: 框架QQ
    :param to_group: 目标群号
    :param from_group: 来源群号
    :param qq: 对方QQ(多个用|分割)
    :return:
    """
    data = {'logonqq': logon_qq, 'togroup': to_group, 'fromgroup': from_group, 'qq': qq}
    return _make_request('invitefriendtogroup', data)


def set_group_member_msg_notice(logon_qq, group, to_qq, notice_type=2):
    """
    置群内消息通知(置群内指定QQ消息通知类型,成功返回真,失败或无权限返回假)

    :param logon_qq: 框架QQ
    :param group: 群号
    :param to_qq: 对方QQ
    :param notice_type: 通知类型(0不接收此人消息,1特别关注,2接收此人消息,默认2)
    :return:
    """
    data = {'logonqq': logon_qq, 'group': group, 'toqq': to_qq, 'type': notice_type}
    return _make_request('setgroupmembermsgrecv', data)


def set_group_name(logon_qq, group, name):
    """
    修改群名称(修改群名称,成功返回真,失败或无权限返回假,需要管理员权限)

    :param logon_qq: 框架QQ
    :param group: 群号
    :param name: 名称(新的群名称)
    :return:
    """
    data = {'logonqq': logon_qq, 'group': group, 'name': name}
    return _make_request('setgroupname', data)


def logout_other_device(logon_qq, is_mobile=False, appid=None):
    """
    下线其他设备(下线本QQ的其他已登录设备)

    :param logon_qq: 框架QQ
    :param is_mobile: 是否移动设备(true,false)
    :param appid: appid(若是移动设备，必填，移动设备的appid可以通过[登录事件_移动设备上线]事件来获取)
    :return:
    """
    data = {'logonqq': logon_qq, 'ismobile': str(is_mobile).lower(), 'appid': appid}
    return _make_request('logoutotherdev', data)


def get_login_url_cookie(logon_qq, url, app_id, da_id):
    """
    登录网页取ck(失败或无权限返回空白)

    :param logon_qq: 框架QQ
    :param url: 回调跳转地址(如QQ空间是：https://h5.qzone.qq.com/mqzone/index)
    :param app_id: appid(如QQ空间是：549000929)
    :param da_id: daid(如QQ空间是：5)
    :return:
    """
    data = {'logonqq': logon_qq, 'url': url, 'appid': app_id, 'daid': da_id}
    return _make_request('getloginurlcookie', data)


def send_group_announcement(logon_qq, group, title, content, path_type='', pic='', video='', is_popup=False,
                            is_need_confirm=False, is_top=False, is_send_to_new_member=False,
                            is_guide_to_set_group_card=False):
    """
    发送群公告(http)

    :param logon_qq: 框架QQ
    :param group: 群号
    :param title: 标题(支持emoji表情,如：\uD83D\uDE01)
    :param content: 内容(支持emoji表情,如：\uD83D\uDE01)
    :param path_type: pic参数类型(path:本地路径,url:网络路径,usermem:共享内存id,其他或留空:BASE64编码数据(不推荐))
    :param pic: 图片(在公告当中插入图片,如果设置了[腾讯视频]参数,则不显示图片只显示视频)
    :param video: 视频(公告当中插入视频,只支持腾讯视频,如：https://v.qq.com/x/cover/4gl2i78zd9idpi0/j0024zknymk.html)
    :param is_popup: 弹窗展示(默认假)
    :param is_need_confirm: 需要确认(默认假)
    :param is_top: 置顶(默认假)
    :param is_send_to_new_member: 发送给新成员(默认假)
    :param is_guide_to_set_group_card: 引导修改群昵称(默认假)
    :return:
    """
    data = {'logonqq': logon_qq, 'group': group, 'title': title, 'content': content, 'type': path_type, 'pic': pic,
            'video': video, 'ispopup': str(is_popup).lower(), 'isneedconfirm': str(is_need_confirm).lower(),
            'istop': str(is_top).lower(), 'issendtonewmember': str(is_send_to_new_member).lower(),
            'isguidetosetgroupcard': str(is_guide_to_set_group_card).lower()}
    return _make_request('sendgroupannouncement', data)


def get_xlz_ver():
    """
    取框架版本(无权限限制)

    :return:
    """
    return _make_request('getxiaolzver')


def get_group_member_info(logon_qq, group, to_qq):
    """
    取群成员信息(获取一个群成员的相关信息)

    :param logon_qq: 框架QQ
    :param group: 群号
    :param to_qq: 对方QQ
    :return:
    """
    data = {'logonqq': logon_qq, 'group': group, 'toqq': to_qq}
    return _make_request('getgroupmemberinfo', data)


def get_wallet_cookie(logon_qq):
    """
    取钱包cookie(敏感API,框架会自动刷新)

    :param logon_qq: 框架QQ
    :return:
    """
    data = {'logonqq': logon_qq}
    return _make_request('getwalletcookie', data)


def get_group_web_cookie(logon_qq):
    """
    取群网页cookie(敏感API,框架会自动刷新)

    :param logon_qq: 框架QQ
    :return:
    """
    data = {'logonqq': logon_qq}
    return _make_request('getgroupwebcookie', data)


def transfer_account(logon_qq, amount, to_qq, pay_pwd, text='', bankcard_id=0, transfer_type=0):
    """
    转账(银行卡支付时，若需要短信验证码，将返回验证码信息，使用API【提交支付验证码】进行验证处理)

    :param logon_qq: 框架QQ
    :param amount: 转账金额(单位分)
    :param to_qq: 对方QQ
    :param text: 转账留言(支持emoji)
    :param transfer_type: 转账类型(0好友转账,1陌生人转账,默认0)
    :param pay_pwd: 支付密码
    :param bankcard_id: 银行卡序列(大于0时使用银行卡支付)
    :return:
    """
    data = {'logonqq': logon_qq, 'amount': amount, 'toqq': to_qq, 'text': text, 'type': transfer_type,
            'paypwd': pay_pwd, 'bankcardid': bankcard_id}
    return _make_request('transferaccount', data)


def withdrawal_balance(logon_qq, amount, pay_pwd, bankcard_id):
    """
    余额提现

    :param logon_qq: 框架QQ
    :param amount: 提现金额(单位分)
    :param pay_pwd: 支付密码
    :param bankcard_id: 银行卡序列(指定提现到的银行卡)
    :return:
    """
    data = {'logonqq': logon_qq, 'amount': amount, 'paypwd': pay_pwd, 'bankcardid': bankcard_id}
    return _make_request('withdrawalbalance', data)


def get_collection_url(logon_qq, amount, description=''):
    """
    取收款链接(返回收款链接,可借此生成收款二维码)

    :param logon_qq: 框架QQ
    :param amount: 收款金额(指定收款金额,单位：分)
    :param description: 说明文本(备注)
    :return:
    """
    data = {'logonqq': logon_qq, 'amount': amount, 'description': description}
    return _make_request('getcollectionurl', data)


def get_short_video_url(chat_type, logon_qq, from_group, from_qq, param, hash1, filename):
    """
    取小视频下载地址(成功返回json含下载链接)

    :param chat_type: 类型(private:私聊,group:群聊)
    :param logon_qq: 框架QQ
    :param from_group: 来源群号(群聊可用)
    :param from_qq: 来源QQ
    :param param: param(可通过文本代码获取)
    :param hash1: hash1(可通过文本代码获取)
    :param filename: 文件名(xxx.mp4,必须带上文件后缀)
    :return:
    """
    data = {'type': chat_type, 'logonqq': logon_qq, 'fromgroup': from_group, 'fromqq': from_qq, 'param': param,
            'hash1': hash1, 'filename': filename}
    return _make_request('getshortvideourl', data)


def upload_short_video(logon_qq, video, pic, group=None, path_type='url', pic_path_type='', width=None, height=None,
                       video_time=None):
    """
    上传小视频(成功返回文本代码,使用的手机录小视频入口,因此不支持较大文件)

    :param logon_qq: 框架QQ
    :param group: 群号(得到的文本代码也可在私聊使用,上传到私聊时,群号可乱填)
    :param path_type: video参数类型(path:本地路径,url:网络路径)
    :param video: 小视频
    :param pic_path_type: pic参数类型(path:本地路径,url:网络路径,usermem:共享内存id,其他或留空:BASE64编码数据(不推荐))
    :param pic: 小视频封面图
    :param width: 宽度
    :param height: 高度
    :param video_time: 时长
    :return:
    """
    if not group:
        group = random.randint(100000000, 1999999999)
    data = {'logonqq': logon_qq, 'group': group, 'type': path_type, 'video': video, 'pictype': pic_path_type,
            'pic': pic, 'width': width, 'height': height, 'time': video_time}
    return _make_request('uploadshortvideo', data)


def get_group_survey(logon_qq, group):
    """
    取群成员概况(成功返回json,含有群上限、群人数、群成员统计概况)

    :param logon_qq: 框架QQ
    :param group: 群号
    :return:
    """
    data = {'logonqq': logon_qq, 'group': group}
    return _make_request('getgroupsurvey', data)


def get_add_friend_verify_type(chat_type, logon_qq, to_qq=None, group=None):
    """
    添加好友_取验证类型(成功返回验证类型json,失败返回403无权限或404未找到对应框架QQ或405框架QQ未登录,ret：101已是好友;2拒绝添加;1需要身份验证;0任何人可添加;4需要回答问题,并返回所有需要回答的问题;3需要正确回答问题,并返回需要回答的问题)

    :param chat_type: 类型(friend:好友,group:群)
    :param logon_qq: 框架QQ
    :param to_qq: 对方QQ(好友可用)
    :param group: 群号(群可用)
    :return:
    """
    data = {'type': chat_type, 'logonqq': logon_qq, 'toqq': to_qq, 'group': group}
    return _make_request('getaddvftype', data)


def group_clock_in(logon_qq, group):
    """
    群聊打卡(返回json)

    :param logon_qq: 框架QQ
    :param group: 群号
    :return:
    """
    data = {'logonqq': logon_qq, 'group': group}
    return _make_request('groupclockin', data)


def group_sign_in(logon_qq, group, param=''):
    """
    群聊签到(成功返回真,失败或无权限返回假,传入附加参数自定义签到内容(附加参数可抓旧版QQ http数据获得))

    :param logon_qq: 框架QQ
    :param group: 群号
    :param param: 附加参数(签到数据,如:template_data=&gallery_info=%7B%22category_id%22%3A9%2C%22page%22%3A0%2C%22pic_id%22%3A124%7D&template_id=%7B%7D&client=2&lgt=0&lat=0&poi=&pic_id=&text=%E5%AD%A6%E4%B9%A0%E6%89%93%E5%8D%A1)
    :return:
    """
    data = {'logonqq': logon_qq, 'group': group, 'param': param}
    return _make_request('groupsignin', data)


def set_group_remark(logon_qq, group, remark=''):
    """
    置群聊备注(成功返回真,失败返回假,无权限返回假)

    :param logon_qq: 框架QQ
    :param group: 群号
    :param remark: 备注
    :return:
    """
    data = {'logonqq': logon_qq, 'group': group, 'remark': remark}
    return _make_request('setgroupremark', data)


def forward_red_packet(logon_qq, red_packet_id, to, chat_type=1):
    """
    红包转发(转发自己的红包到其他群或好友或讨论组)

    :param logon_qq: 框架QQ
    :param red_packet_id: 红包ID
    :param to: 目标对象(以Type类型为准,如果是1则判断为QQ号2则判断为群号3则判断为讨论组号)
    :param chat_type: Type(1为好友,2为群,3为讨论组)
    :return:
    """
    data = {'logonqq': logon_qq, 'redpacketid': red_packet_id, 'to': to, 'type': chat_type}
    return _make_request('forwardredpacket', data)


def send_packet(logon_qq, sso_seq, packet, max_wait_time=0):
    """
    发送数据包(向腾讯服务器发送数据包(完整的原始包),无权限等返回假,加密秘钥通过【取sessionkey】API获取,返回BASE64编码)

    :param logon_qq: 框架QQ
    :param sso_seq: 包体序号(ssoseq,通过【请求ssoseq】API获取)
    :param max_wait_time: 最大等待时长(毫秒,不填或小于0时不等待返回包,大于0时等待返回包)
    :param packet: 数据(BASE64编码)
    :return:
    """
    data = {'logonqq': logon_qq, 'ssoseq': sso_seq, 'maxwaittime': max_wait_time, 'packet': packet}
    return _make_request('sendpacket', data)


def get_sso_seq(logon_qq):
    """
    请求ssoseq(无权限等返回0)

    :param logon_qq: 框架QQ
    :return:
    """
    data = {'logonqq': logon_qq}
    return _make_request('getssoseq', data)


def get_session_key(logon_qq):
    """
    取sessionkey

    :param logon_qq: 框架QQ
    :return:
    """
    data = {'logonqq': logon_qq}
    return _make_request('getsessionkey', data)


def get_bkn_gtk(logon_qq, custom_bkn_gtk=''):
    """
    获取bkn_gtk(返回网页用到的bkn或者gtk,也可以自定义计算的值)

    :param logon_qq: 框架QQ
    :param custom_bkn_gtk: 自定义bkn_gtk(如果此参数不为空值则提交自定义值,否则框架返回内部值)
    :return:
    """
    data = {'logonqq': logon_qq, 'custombkngtk': custom_bkn_gtk}
    return _make_request('getbkn_gtk', data)


def set_add_friend_verify_method(logon_qq, method=3, q_and_a=''):
    """
    置好友验证方式(修改添加好友的方式,成功返回真,失败或无权限返回假)

    :param logon_qq: 框架QQ
    :param method: 验证方式(1：禁止任何人添加,2：允许任何人添加,3：需要验证信息,4：需要正确回答问题,5：需要回答问题并由我确认)
    :param q_and_a: Q_and_A(可空,如果类型为4则填写问题和答案用‘|’分割,如果类型为5则根据情况填写问题至少一个最多三个问题,用‘|’分割)
    :return:
    """
    data = {'logonqq': logon_qq, 'method': method, 'qa': q_and_a}
    return _make_request('setaddfvfmethod', data)


def upload_photo_wall(pic, logon_qq, path_type=''):
    """
    上传照片墙图片(上传一照片至照片墙,成功返回带有‘上传成功’字样的json,失败或无权限返回json)

    :param path_type: pic参数类型(path:本地路径,url:网络路径,usermem:共享内存id,其他或留空:BASE64编码数据(不推荐))
    :param pic: 图片
    :param logon_qq: 框架QQ
    :return:
    """
    data = {'type': path_type, 'pic': pic, 'logonqq': logon_qq}
    return _make_request('uploadphotowall', data)


def pay(logon_qq, qrcode_url, pay_pwd, bankcard_id=0):
    """
    付款(银行卡支付时，若需要短信验证码，将返回验证码信息，使用API【提交支付验证码】进行验证处理)

    :param logon_qq: 框架QQ
    :param qrcode_url: QrcodeUrl(QQ钱包支付二维码内容(需要自己识别二维码,将识别结果填入))
    :param bankcard_id: 银行卡序列(大于0则表示使用银行卡支付反之用余额支付)
    :param pay_pwd: 支付密码
    :return:
    """
    data = {'logonqq': logon_qq, 'qrcodeurl': qrcode_url, 'bankcardid': bankcard_id, 'paypwd': pay_pwd}
    return _make_request('pay', data)


def reset_pay_password(logon_qq, old_pwd, new_pwd):
    """
    修改支付密码(修改QQ钱包支付密码,成功返回json retcode=0 ,失败或无权限返回其他值)

    :param logon_qq: 框架QQ
    :param old_pwd: 原密码(6位数字原密码)
    :param new_pwd: 新密码(6位数字新密码)
    :return:
    """
    data = {'logonqq': logon_qq, 'oldpwd': old_pwd, 'newpwd': new_pwd}
    return _make_request('resetpaypwd', data)


def search_account(logon_qq, keyword):
    """
    账号搜索(对一个关键词进行简略搜索,通过关键词一般返回3个QQ号信息和群信息,成功返回json retcode=0 ,失败或无权限返回其他值)

    :param logon_qq: 框架QQ
    :param keyword: 关键词(关键词，支持QQ号、群号、昵称等，支持emoji)
    :return:
    """
    data = {'logonqq': logon_qq, 'keyword': keyword}
    return _make_request('searchaccount', data)


def get_red_packet_detail(logon_qq, red_packet, packet_type=0, from_group=None):
    """
    获取红包领取详情(只有领取过该红包才能成功查询,返回腾讯原始json数据)

    :param logon_qq: 框架QQ
    :param from_group: 来源群号(红包为好友红包时,此参数可以省略,为讨论组时此处为讨论组Id)
    :param red_packet: 红包文本代码
    :param packet_type: 红包类型(1:好友,2:群,3:讨论组,其他:群临时)
    :return:
    """
    data = {'logonqq': logon_qq, 'fromgroup': from_group, 'redpacket': red_packet, 'type': packet_type}
    return _make_request('getredpacketdetail', data)


def get_extension_info(logon_qq, to_qq):
    """
    取扩列资料(取对方的扩列资料,即使对方隐藏也可以查询)

    :param logon_qq: 框架QQ
    :param to_qq: 对方QQ
    :return:
    """
    data = {'logonqq': logon_qq, 'toqq': to_qq}
    return _make_request('getextensioninfo', data)


def get_info_show_set(logon_qq, to_qq):
    """
    取资料展示设置(支持查询他人的设置)

    :param logon_qq: 框架QQ
    :param to_qq: 对方QQ
    :return:
    """
    data = {'logonqq': logon_qq, 'toqq': to_qq}
    return _make_request('getinfoshowset', data)


def set_info_show_set(logon_qq=0, sex=0, age=0, birthday=0, constellation=0, occupation=0, company=0, school=0,
                      location=0, hometown=0, email=0, description=0, 我的王者战绩=True, 我的粉籍=True, 个性标签=True,
                      匿问我答=True, 人生成就=True, 最近常听=True, 收到礼物=True, 最近在玩=True, 我的音乐盒=True,
                      随心贴=True, 我的小世界=True, 我的微视=True, 扩列资料=True):
    """
    设置资料展示(设置QQ资料卡显示什么、不显示什么,注意！数据每一项都必须被定义！,整数型(0所有人可见 1仅好友可见 2所有人不可见),逻辑型(false 关闭 true 开启),类型请参考getinfoshowset)

    :param logon_qq: 框架QQ
    :param sex: 性别
    :param age: 年龄
    :param birthday: 生日
    :param constellation: 星座
    :param occupation: 职业
    :param company: 公司
    :param school: 学校
    :param location: 所在地
    :param hometown: 故乡
    :param email: 邮箱
    :param description: 个人说明
    :param 我的王者战绩:
    :param 我的粉籍:
    :param 个性标签:
    :param 匿问我答:
    :param 人生成就:
    :param 最近常听:
    :param 收到礼物:
    :param 最近在玩:
    :param 我的音乐盒:
    :param 随心贴:
    :param 我的小世界:
    :param 我的微视:
    :param 扩列资料:
    :return:
    """
    data = {'logonqq': logon_qq, 'sex': sex, 'age': age, 'birthday': birthday, 'constellation': constellation,
            'occupation': occupation, 'company': company, 'school': school, 'location': location, 'hometown': hometown,
            'email': email, 'description': description, '我的王者战绩': str(我的王者战绩).lower(),
            '我的粉籍': str(我的粉籍).lower(), '个性标签': str(个性标签).lower(), '匿问我答': str(匿问我答).lower(),
            '人生成就': str(人生成就).lower(), '最近常听': str(最近常听).lower(), '收到礼物': str(收到礼物).lower(),
            '最近在玩': str(最近在玩).lower(), '我的音乐盒': str(我的音乐盒).lower(), '随心贴': str(随心贴).lower(),
            '我的小世界': str(我的小世界).lower(), '我的微视': str(我的微视).lower(), '扩列资料': str(扩列资料).lower()}
    return _make_request('setinfoshowset', data)


def get_logon_device_info(logon_qq):
    """
    获取当前登录设备信息

    :param logon_qq: 框架QQ
    :return:
    """
    data = {'logonqq': logon_qq}
    return _make_request('getlogondevinfo', data)


def photo_ocr(logon_qq, url):
    """
    提取图片文字(tcp)

    :param logon_qq: 框架QQ
    :param url: 图片地址(需要有效的图片地址,支持https)
    :return:
    """
    data = {'logonqq': logon_qq, 'url': url}
    return _make_request('photoocr', data)


def tea_crypt(crypt_type, data, key):
    """
    TEA加解密(无权限限制,参考传回结果)

    :param crypt_type: 类型(encry:加密,decry:解密)
    :param data: 内容
    :param key: 秘钥
    :return:
    """
    data = {'type': crypt_type, 'data': data, 'key': key}
    return _make_request('teacrypt', data)


def red_packet_crypt(crypt_type, data_str, data_random):
    """
    红包数据加密(无权限限制 DES ECB No Padding)

    :param crypt_type: 类型(encry:加密,decry:解密)
    :param data_str: str
    :param data_random: random
    :return:
    """
    data = {'type': crypt_type, 'str': data_str, 'random': data_random}
    return _make_request('redpacketcrypt', data)


def get_red_packet_msg_no(logon_qq):
    """
    红包msgno计算(无权限限制)

    :param logon_qq: 目标QQ
    :return:
    """
    data = {'logonqq': logon_qq}
    return _make_request('getredpacketmsgno', data)


def get_qzone_cookie(logon_qq):
    """
    取QQ空间cookie(敏感API,框架会自动刷新)

    :param logon_qq: 框架QQ
    :return:
    """
    data = {'logonqq': logon_qq}
    return _make_request('getqzonecookie', data)


def query_url_security(logon_qq, url):
    """
    查询网址安全性(403无权限,404框架QQ不存在,405框架QQ未登录,0正常访问,-1查询失败,1包含不安全内容,2非官方页面,3未知状态)

    :param logon_qq: 框架QQ
    :param url: 网址
    :return:
    """
    data = {'logonqq': logon_qq, 'url': url}
    return _make_request('queryurlsecurity', data)


def get_card_msg(card):
    """
    取卡片消息代码(无权限限制,传入卡片消息文本代码,返回卡片消息代码)

    :param card: 卡片消息文本代码(如:[customNode,key=xx,val=xx])
    :return:
    """
    data = {'card': card}
    return _make_request('getcardmsg', data)


def mute_group_anonymous(logon_qq, group, anonymous_name, anonymous_id, mute_time=0):
    """
    禁言群匿名(失败或无权限返回假)

    :param logon_qq: 框架QQ
    :param group: 群号
    :param anonymous_name: 匿名昵称(可通过群聊消息数据获得)
    :param anonymous_id: 匿名标识(可通过群聊消息数据获得,同一个匿名每条消息发送时的标识都不同,解除禁言时,此为对方最后一次发言时的标识)
    :param mute_time: 禁言时长(单位：秒，为0时解除禁言)
    :return:
    """
    data = {'logonqq': logon_qq, 'group': group, 'anonymousname': anonymous_name, 'anonymousid': anonymous_id,
            'time': mute_time}
    return _make_request('mutegroupanonymous', data)


def get_red_packet_private_normal(logon_qq, from_qq, red_packet, packet_type=0):
    """
    领取私聊普通红包(仅仅支持好友、群临时，仅限于普通红包)

    :param logon_qq: 框架QQ
    :param from_qq: 来源QQ(红包发送者QQ)
    :param red_packet: 红包文本代码(红包消息的文本代码)
    :param packet_type: 类型(0好友红包,1群临时红包)
    :return:
    """
    data = {'logonqq': logon_qq, 'fromqq': from_qq, 'redpacket': red_packet, 'type': packet_type}
    return _make_request('getredpacket/private/normal', data)


def get_red_packet_group_exclusive(logon_qq, group, from_qq, red_packet):
    """
    领取群聊专属红包(仅仅支持群聊下的专属红包(当然指的是给自己的专属红包))

    :param logon_qq: 框架QQ
    :param group: 来源群号(红包来源群号)
    :param from_qq: 来源QQ(红包发送者QQ)
    :param red_packet: 红包文本代码(红包消息的文本代码)
    :return:
    """
    data = {'logonqq': logon_qq, 'group': group, 'fromqq': from_qq, 'redpacket': red_packet}
    return _make_request('getredpacket/group/exclusive', data)


def reply_consult(logon_qq, to_qq, token, msg):
    """
    回复QQ咨询会话(当对方通过QQ咨询联系你,但是对方未开启QQ咨询时,只能通过此API进行回复)

    :param logon_qq: 框架QQ
    :param to_qq: 对方QQ
    :param token: 会话Token(私聊消息数据.会话token,具有时效性,是对方推送的)
    :param msg: 消息内容
    :return:
    """
    data = {'logonqq': logon_qq, 'toqq': to_qq, 'token': token, 'msg': msg}
    return _make_request('replyconsult', data)


def send_subscription_msg(logon_qq, subscription_id, msg):
    """
    发送订阅号私聊消息

    :param logon_qq: 框架QQ
    :param subscription_id: 订阅号Id
    :param msg: 消息内容
    :return:
    """
    data = {'logonqq': logon_qq, 'subscriptionid': subscription_id, 'msg': msg}
    return _make_request('sendsubscriptionmsg', data)


def get_discussion_name(discussion_id):
    """
    取讨论组名称_从缓存(失败或无权限返回空,从缓存取讨论组名(当取出为空时,先使用【取讨论组成员列表】,之后缓存内便有讨论组的名称))

    :param discussion_id: 讨论组Id(同：群消息数据.消息群号)
    :return:
    """
    data = {'discussionid': discussion_id}
    return _make_request('getdiscussionname', data)


def force_get_anonymous_id(logon_qq, group):
    """
    强制取自身匿名Id(禁止在其他设备更换匿名,否则匿名相关功能无效)

    :param logon_qq: 框架QQ
    :param group: 群号
    :return:
    """
    data = {'logonqq': logon_qq, 'group': group}
    return _make_request('forcegetanonymousid', data)


def get_subscription_list(logon_qq):
    """
    取订阅号列表

    :param logon_qq: 框架QQ
    :return:
    """
    data = {'logonqq': logon_qq}
    return _make_request('getsubscriptionlist', data)


def get_discussion_list(logon_qq):
    """
    取讨论组列表

    :param logon_qq: 框架QQ
    :return:
    """
    data = {'logonqq': logon_qq}
    return _make_request('getdiscussionlist', data)


def invite_friend_to_discussion(logon_qq, discussion_id, qq, from_group=None):
    """
    邀请好友加入讨论组(失败或无权限返回假)

    :param logon_qq: 框架QQ
    :param discussion_id: 目标讨论组Id
    :param qq: 邀请QQ(多个QQ用|分割)
    :param from_group: 来源群号(若邀请QQ来源是群成员，则在此说明群号，否则留空，表明来源是好友)
    :return:
    """
    data = {'logonqq': logon_qq, 'discussionid': discussion_id, 'qq': qq, 'fromgroup': from_group}
    return _make_request('invitefriendtodiscussion', data)


def get_xlz_expire():
    """
    取框架到期时间(无权限限制,返回示例：2025/1/1 00:00:00,年月日无补零,时分秒有补零)

    :return:
    """
    return _make_request('getxlzexpire')


def send_discussion_red_packet(packet_type, logon_qq, count, amount, discussion_id, text, pay_pwd, bankcard_id=0,
                               skin_id=None, to=None, is_avg=False):
    """
    发送讨论组红包(银行卡支付时，若需要短信验证码，将返回验证码信息，使用API【提交支付验证码】进行验证处理)

    :param packet_type: 类型(norm:普通红包,lucky:拼手气红包,key:口令红包,draw:画图红包,audio:语音红包,jielong:接龙红包,exclusive:专属红包,rareword:生僻字红包)
    :param logon_qq: 框架QQ
    :param count: 总数量
    :param amount: 总金额(单位分)
    :param discussion_id: 讨论组Id
    :param text: 文本
    :param skin_id: 红包皮肤Id(1522光与夜之恋,1527代号:三国(打了一辈子仗),1525街霸:对决,1518代号:三国(俺送红包来了),1476天涯明月刀,1512一人之下。其他皮肤id自己找,仅普通红包|拼手气红包可用)
    :param to: 领取人(仅专属红包可用)
    :param is_avg: 是否均分(仅专属红包可用)
    :param pay_pwd: 支付密码
    :param bankcard_id: 银行卡序列(大于0时使用银行卡支付)
    :return:
    """
    data = {'type': packet_type, 'logonqq': logon_qq, 'count': count, 'amount': amount, 'discussionid': discussion_id,
            'text': text, 'skinid': skin_id, 'to': to, 'isavg': str(is_avg).lower(), 'paypwd': pay_pwd,
            'bankcardid': bankcard_id}
    return _make_request('senddiscussionredpacket', data)


def get_discussion_not_recv_red_packet_list(logon_qq, discussion_id):
    """
    取讨论组未领红包(成功返回未领红包，注意：使用此API获取的红包只能用手Q上"讨论组未领红包"入口的http请求领取)

    :param logon_qq: 框架QQ
    :param discussion_id: 讨论组Id
    :return:
    """
    data = {'logonqq': logon_qq, 'discussionid': discussion_id}
    return _make_request('getdiscussionnoreredpacketlist', data)


def send_consult(logon_qq, to_qq, msg):
    """
    发送QQ咨询会话(当对方开启了QQ咨询,则可通过QQ咨询主动向对方发送消息,若对方没有开启QQ咨询,则只能使用API【回复QQ咨询会话】进行回复)

    :param logon_qq: 框架QQ
    :param to_qq: 对方QQ
    :param msg: 消息内容
    :return:
    """
    data = {'logonqq': logon_qq, 'toqq': to_qq, 'msg': msg}
    return _make_request('sendconsult', data)


def new_group(logon_qq, qq, from_group=None):
    """
    创建群聊(成功参考传回新群群号)

    :param logon_qq: 框架QQ
    :param qq: 邀请QQ(多个用|分割)
    :param from_group: 来源群号(若邀请QQ来源是群成员，则在此说明群号，否则留空，表明来源是好友)
    :return:
    """
    data = {'logonqq': logon_qq, 'qq': qq, 'fromgroup': from_group}
    return _make_request('newgroup', data)


def get_group_app_list(logon_qq, group):
    """
    取群应用列表(成功返回群应用数量)

    :param logon_qq: 框架QQ
    :param group: 群号
    :return:
    """
    data = {'logonqq': logon_qq, 'group': group}
    return _make_request('getgroupapplist', data)


def exit_discussion(logon_qq, discussion_id):
    """
    退出讨论组(失败或无权限返回假)

    :param logon_qq: 框架QQ
    :param discussion_id: 讨论组Id
    :return:
    """
    data = {'logonqq': logon_qq, 'discussionid': discussion_id}
    return _make_request('exitdiscussion', data)


def set_add_group_request_recv(logon_qq, group, to_qq, is_recv=True):
    """
    群验证消息接收设置(设置指定管理员是否接收群验证消息,失败或无权限返回假,需要机器人为群主,否则无法设置)

    :param logon_qq: 框架QQ
    :param group: 群号
    :param to_qq: 对方QQ(管理员QQ)
    :param is_recv: 是否接收验证消息(true,false)
    :return:
    """
    data = {'logonqq': logon_qq, 'group': group, 'toqq': to_qq, 'isrecv': str(is_recv).lower()}
    return _make_request('setaddgrouprequestrecv', data)


def transfer_group(logon_qq, group, to_qq):
    """
    转让群(需要机器人为群主,需要新群主具备转让资格)

    :param logon_qq: 框架QQ
    :param group: 群号
    :param to_qq: 对方QQ(新群主QQ,可以是管理员、普通成员,只要对方有转让资格即可)
    :return:
    """
    data = {'logonqq': logon_qq, 'group': group, 'toqq': to_qq}
    return _make_request('transfergroup', data)


def set_friend_remark(logon_qq, to_qq, remark):
    """
    修改好友备注(失败或无权限返回假)

    :param logon_qq: 框架QQ
    :param to_qq: 对方QQ(好友QQ)
    :param remark: 备注(新的备注)
    :return:
    """
    data = {'logonqq': logon_qq, 'toqq': to_qq, 'remark': remark}
    return _make_request('setfriendremark', data)


def kick_discussion_member(logon_qq, discussion_id, to_qq):
    """
    删除讨论组成员(失败或无权限返回假,需要机器人为讨论组拥有者,否则没有权限)

    :param logon_qq: 框架QQ
    :param discussion_id: 讨论组Id
    :param to_qq: 对方QQ
    :return:
    """
    data = {'logonqq': logon_qq, 'discussionid': discussion_id, 'toqq': to_qq}
    return _make_request('kickdiscussionmember', data)


def get_qq_avatar(to_qq, is_hd=True):
    """
    取QQ头像(获取QQ头像,无权限限制,默认返回低像素链接,注意部分QQ,比如透明头像的QQ,是没有高清头像的,取出来是鹅,只能取低像素头像)

    :param to_qq: 对方QQ
    :param is_hd: 是否高清原图(true,false)
    :return:
    """
    data = {'toqq': to_qq, 'ishd': str(is_hd).lower()}
    return _make_request('getqqfacepic', data)


def get_group_avatar(group):
    """
    取群头像(无权限限制)

    :param group: 目标群号(讨论组、多人群没有群头像,取出来是腾讯默认群头像图片)
    :return:
    """
    data = {'group': group}
    return _make_request('getgroupfacepic', data)


def get_big_face_pic_url(big_face, width=300, height=300):
    """
    取大表情图片下载地址(无权限限制,支持付费表情包)

    :param big_face: 大表情文本代码(大表情其实就是表情包表情)
    :param width: 长(默认300(部分付费表情包可能是260,但基本上都是300,遇到取出的链接无效时,请尝试更改此值))
    :param height: 宽(默认300(部分付费表情包可能是260,但基本上都是300,遇到取出的链接无效时,请尝试更改此值))
    :return:
    """
    data = {'bigface': big_face, 'width': width, 'height': height}
    return _make_request('getbigfacepicurl', data)


def send_group_collection(logon_qq, group, payer_list, text):
    """
    拉起群收款(成功时,参考传回收款订单号(不支持讨论组,讨论组相关功能[AA收款]已被腾讯下架))

    :param logon_qq: 框架QQ
    :param group: 群号
    :param payer_list: 待付款成员(自定义付款成员和付款金额,json,例如{"list":[{"qq":123456,"needpay":2000},{"qq":234567,"needpay":4000}]},qq为付款者qq,needpgay为待付款金额,单位分)
    :param text: 收款留言(可以写明收款理由)
    :return:
    """
    data = {'logonqq': logon_qq, 'group': group, 'payerlist': payer_list, 'text': text}
    return _make_request('sendgroupcollection', data)


def stop_group_collection(logon_qq, order_num):
    """
    结束群收款(只能结束自己拉起的)

    :param logon_qq: 框架QQ
    :param order_num: 收款订单号(待结束的订单号)
    :return:
    """
    data = {'logonqq': logon_qq, 'ordernum': order_num}
    return _make_request('stopgroupcollection', data)


def query_group_collection_state(logon_qq, order_num):
    """
    查询群收款状态(支持查询他人拉起的群收款,成功时,参考传回数据)

    :param logon_qq: 框架QQ
    :param order_num: 收款订单号(待查询的收款订单号)
    :return:
    """
    data = {'logonqq': logon_qq, 'ordernum': order_num}
    return _make_request('querygroupcollectionstate', data)


def pay_group_collection(logon_qq, from_qq, order_num, pay_amount, pay_pwd, bankcard_id=0):
    """
    支付群收款(银行卡支付时，若需要短信验证码，将返回验证码信息，使用API【提交支付验证码】进行验证处理)

    :param logon_qq: 框架QQ
    :param from_qq: 收款发起人
    :param order_num: 收款订单号(群收款订单号)
    :param pay_amount: 支付金额(单位分,必须填入正确的值)
    :param pay_pwd: 支付密码
    :param bankcard_id: 银行卡序列(大于0时使用银行卡支付)
    :return:
    """
    data = {'logonqq': logon_qq, 'fromqq': from_qq, 'ordernum': order_num, 'payamount': pay_amount, 'paypwd': pay_pwd,
            'bankcardid': bankcard_id}
    return _make_request('paygroupcollection', data)


def remind_group_collection(logon_qq, order_num):
    """
    群收款_催单

    :param logon_qq: 框架QQ
    :param order_num: 收款订单号
    :return:
    """
    data = {'logonqq': logon_qq, 'ordernum': order_num}
    return _make_request('remindgroupcollection', data)


def get_friend_diy_card(logon_qq, to_qq):
    """
    取好友Diy名片数据(支持陌生人,失败或无权限或对方未设置返回假,参考传回Diy名片数据)

    :param logon_qq: 框架QQ
    :param to_qq: 对方QQ
    :return:
    """
    data = {'logonqq': logon_qq, 'toqq': to_qq}
    return _make_request('getfrienddiycard', data)


def set_diy_card(logon_qq, data):
    """
    设置Diy名片

    :param logon_qq: 框架QQ
    :param data: Diy名片数据(特定格式,自己抓http包,不能直接用【取好友Diy名片数据】的返回结果)
    :return:
    """
    data = {'logonqq': logon_qq, 'data': data}
    return _make_request('setdiycard', data)


def pay_for_another(logon_qq, order_num, pay_amount, pay_pwd, bankcard_id=0):
    """
    支付代付请求(银行卡支付时，若需要短信验证码，将返回验证码信息，使用API【提交支付验证码】进行验证处理)

    :param logon_qq: 框架QQ
    :param order_num: 代付订单号(即:tokenid)
    :param pay_amount: 支付金额(单位分,必须填入正确的值)
    :param pay_pwd: 支付密码
    :param bankcard_id: 银行卡序列(大于0时使用银行卡支付)
    :return:
    """
    data = {'logonqq': logon_qq, 'ordernum': order_num, 'payamount': pay_amount, 'paypwd': pay_pwd,
            'bankcardid': bankcard_id}
    return _make_request('payforanother', data)


def query_pay_for_another_state(logon_qq, order_num, data):
    """
    查询代付状态(成功返回原始json数据,自行解析)

    :param logon_qq: 框架QQ
    :param order_num: 代付订单号(即:tokenid)
    :param data: 代付数据(即:data)
    :return:
    """
    data = {'logonqq': logon_qq, 'ordernum': order_num, 'data': data}
    return _make_request('querypayforanotherstate', data)


def new_pay_for_another(logon_qq, order_num, qq):
    """
    拉起代付(成功返回原始json数据,自行解析)

    :param logon_qq: 框架QQ
    :param order_num: 订单号(即:tokenid,用QQ钱包进行充值话费等操作时,拉起支付,即可获得订单号(tokenid),随后传入即可拉起代付)
    :param qq: 代付QQ列表(多个QQ以|分割)
    :return:
    """
    data = {'logonqq': logon_qq, 'ordernum': order_num, 'qq': qq}
    return _make_request('newpayforanother', data)


def get_friend_energy_and_qid(logon_qq, to_qq):
    """
    取好友能量值与QID(支持陌生人,失败或无权限返回假,只要对方设置了QID显示或能量值显示则返回真)

    :param logon_qq: 框架QQ
    :param to_qq: 对方QQ
    :return:
    """
    data = {'logonqq': logon_qq, 'toqq': to_qq}
    return _make_request('getfriendenergyandqid', data)


def text_to_audio(logon_qq, text):
    """
    文字转语音(音源与登录QQ的性别有关,返回BASE64编码)

    :param logon_qq: 框架QQ
    :param text: 文本内容
    :return:
    """
    data = {'logonqq': logon_qq, 'text': text}
    return _make_request('text2audio', data)


def translate(logon_qq, src_lang, dst_lang, text):
    """
    翻译(语种代码列表:http://www.lingoes.cn/zh/translator/langcode.htm)

    :param logon_qq: 框架QQ
    :param src_lang: 源语言语种(如:zh (中文))
    :param dst_lang: 目标语言语种(如:ko (韩语))
    :param text: 原文
    :return:
    """
    data = {'logonqq': logon_qq, 'srclang': src_lang, 'dstlang': dst_lang, 'text': text}
    return _make_request('translate', data)


def amr_encode(data_type, data):
    """
    amr编码(返回共享内存ID)

    :param data_type: data参数类型(path:本地路径 url:网络路径 usermem:共享内存id 其他或留空:BASE64编码数据(不推荐))
    :param data: 数据
    :return:
    """
    data = {'type': data_type, 'data': data}
    return _make_request('amrencode', data)


def silk_encode(data_type, data):
    """
    silk编码(返回共享内存ID)

    :param data_type: data参数类型(path:本地路径 url:网络路径 usermem:共享内存id 其他或留空:BASE64编码数据(不推荐))
    :param data: 数据
    :return:
    """
    data = {'type': data_type, 'data': data}
    return _make_request('silkencode', data)


def silk_decode(data_type, data):
    """
    silk解码(返回共享内存ID)

    :param data_type: data参数类型(path:本地路径 url:网络路径 usermem:共享内存id 其他或留空:BASE64编码数据(不推荐))
    :param data: 数据
    :return:
    """
    data = {'type': data_type, 'data': data}
    return _make_request('silkdecode', data)


class UserMem_API:
    """
    共享内存

    本功能支持在插件中创建若干块内存，可使用HTTP API操作和访问这些内存块

    *注意:请务必及时释放内存块！！！

    offset是当前数据偏移量
    """

    @staticmethod
    def create(size, desc=None):
        """
        创建内存块

        返回内存块ID

        注意:内存块ID不是内存指针

        :param size: 内存块大小
        :param desc: 备注
        :return:
        """
        params = {'type': 'alloc', 'size': size, 'desc': desc}
        return _make_request('adv/usermem', params=params)

    @staticmethod
    def free(mem_id):
        """
        删除内存块

        :param mem_id: 内存块ID
        :return:
        """
        params = {'type': 'free', 'id': mem_id}
        return _make_request('adv/usermem', params=params)

    @staticmethod
    def read(mem_id, length):
        """
        读内存块内容

        注意:从当前offset开始读，读完后offset将向后移动实际读取长度的大小，若欲读取长度大于实际可读长度则会截断

        :param mem_id: 内存块ID
        :param length: 长度
        :return:
        """
        params = {'type': 'read', 'id': mem_id, 'length': length}
        return _make_request('adv/usermem', params=params, ignore_errors=True)

    @staticmethod
    def write(mem_id, data: bytes):
        """
        写内存块

        注意:从当前offset开始写，写完后offset将向后移动实际写入长度的大小，应使用raw post提交数据，若欲写入数据长度大于实际可写数据长度则会截断，返回实际写入的长度

        :param mem_id: 内存块ID
        :param data: 数据
        :return:
        """
        params = {'type': 'write', 'id': mem_id}
        return _make_request('adv/usermem', data, params)

    @staticmethod
    def set_offset(mem_id, offset):
        """
        设置offset

        :param mem_id: 内存块ID
        :param offset: 新的offset
        :return:
        """
        params = {'type': 'offset', 'id': mem_id, 'offset': offset}
        return _make_request('adv/usermem', params=params)

    @staticmethod
    def query(mem_id):
        """
        查询内存块

        :param mem_id: 内存块ID
        :return:
        """
        params = {'type': 'query', 'id': mem_id}
        return _make_request('adv/usermem', params=params)

    @staticmethod
    def list():
        """
        内存块列表

        :return:
        """
        params = {'type': 'list'}
        return _make_request('adv/usermem', params=params)


class SchWork_API:
    """
    本功能支持设置定时任务，定时产生事件，通过ws或事件上报发送，类型为ScheduleWork

    返回任务ID
    """

    @staticmethod
    def create(timestamp, arg, desc=None):
        """
        创建任务(一次性)

        返回任务ID

        :param timestamp: 触发任务时间戳(10位)
        :param arg: 产生事件时附带参数
        :param desc: 备注
        :return:
        """
        params = {'type': 'create', 'time': timestamp, 'arg': arg, 'desc': desc}
        return _make_request('adv/schwork', params=params)

    @staticmethod
    def remove(task_id):
        """
        删除任务

        :param task_id: 任务ID
        :return:
        """
        params = {'type': 'remove', 'id': task_id}
        return _make_request('adv/schwork', params=params)

    @staticmethod
    def query(task_id):
        """
        查询任务

        :param task_id: 任务ID
        :return:
        """
        params = {'type': 'query', 'id': task_id}
        return _make_request('adv/schwork', params=params)

    @staticmethod
    def list():
        """
        任务列表

        :return:
        """
        params = {'type': 'list'}
        return _make_request('adv/schwork', params=params)
