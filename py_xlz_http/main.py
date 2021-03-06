# coding=utf-8
"""main"""
import inspect
import json
import logging.handlers
import os
import re
import sys
import threading
import traceback
import typing
from functools import wraps

import py_xlz_http.types as types

# usc2_mode = False  # 暂时没用

_private_handlers = []  # type: list[dict]
_group_handlers = []  # type: list[dict]
_event_handlers = []  # type: list[dict]
_schedule_work_handlers = []  # type: list[dict]


def _get_logger():
    tmp_logger = logging.getLogger('py-xlz-http')
    formatter = logging.Formatter("%(asctime)s - %(filename)s:%(lineno)d - %(levelname)s - %(message)s")
    tmp_logger.setLevel(logging.DEBUG)
    # basic logger stdout
    basic_logger = logging.getLogger()
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(formatter)
    stdout_handler.setLevel(logging.INFO)
    basic_logger.addHandler(stdout_handler)
    # file handler
    if not os.path.exists('./logs'):
        os.mkdir('./logs')
    log_file_handler = logging.handlers.TimedRotatingFileHandler(
        filename="./logs/py-xlz-http.log", when="midnight", encoding='utf-16')
    log_file_handler.suffix = "%Y-%m-%d.log"
    log_file_handler.extMatch = re.compile(r"^\d{4}-\d{2}-\d{2}.log$")
    log_file_handler.setFormatter(formatter)
    log_file_handler.setLevel(logging.DEBUG)
    tmp_logger.addHandler(log_file_handler)
    return tmp_logger


logger = _get_logger()


def _get_stack() -> str:
    """获取执行堆栈并格式化"""
    stack = []
    stacks = inspect.stack()
    stacks.reverse()
    for i in stacks[:-1]:
        stack.append(f'{i.filename[i.filename.rfind(os.sep) + 1:]}:{i.lineno}')
    return ' → '.join(stack)


def _process_msg(msg_, msg_type_):
    """投递新消息"""

    def call_event(msg, msg_type):
        try:
            handlers = None
            if msg_type == 1:  # 私聊
                handlers = _private_handlers
            elif msg_type == 2:  # 群聊
                handlers = _group_handlers
            elif msg_type == 3:  # 事件
                handlers = _event_handlers
            elif msg_type == 4:  # 定时任务
                handlers = _schedule_work_handlers
                # 参数不一样，单独处理（太惨了）
                for handler in handlers:
                    if (handler['arg'] is None) or (msg.arg == handler['arg']):
                        if handler['handler'](msg) is True:  # 调用事件处理函数，返回true停止调用其他函数
                            logger.info(f'[{_get_stack()}]已拦截消息 [{msg}]')
                            break
                return

            for handler in handlers:
                if (handler['bots'] is None) or (msg.logon_qq in handler['bots']):
                    if (handler['regexp'] is None) or (re.search(handler['regexp'], msg.msg.text)):
                        if (handler['function'] is None) or (handler['function'](msg)):
                            if handler['handler'](msg) is True:  # 调用事件处理函数，返回true停止调用其他函数
                                logger.info(f'[{_get_stack()}]已拦截消息 [{msg}]')
                                break
        except:
            logger.error(f'[{_get_stack()}]调用消息处理函数时出错\n' + traceback.format_exc())

    threading.Thread(target=call_event, args=(msg_, msg_type_)).start()  # 投递线程


def update_msg(json_str: str):
    """
    处理新消息

    :param json_str: http api传入的json消息内容
    """
    try:
        j = json.loads(json_str)
    except:
        logger.error('json解析失败\n' + traceback.format_exc())
    else:
        try:
            if j['type'] == 'privatemsg':
                msg = types.PrivateMsg(j)
                msg_type = 1
            elif j['type'] == 'groupmsg':
                msg = types.GroupMsg(j)
                msg_type = 2
            elif j['type'] == 'eventmsg':
                msg = types.EventMsg(j)
                msg_type = 3
            elif j['type'] == 'schedulework':
                msg = types.ScheduleWork(j)
                msg_type = 4
            else:
                raise ValueError('This json is not a message data')
        except:
            logger.error('消息数据解析失败\n' + traceback.format_exc())
        else:
            logger.info(str(msg))
            _process_msg(msg, msg_type)


def private_msg_handler(
        bots=None,  # type: typing.Optional[list[int]]
        regexp=None,  # type: typing.Union[None, str, re.Pattern]
        function=None  # type: typing.Optional[typing.Callable[[types.PrivateMsg], bool]]
):
    """
    私聊消息处理 函数装饰器

    示例：

    @private_msg_handler(bots=[3076823485]) #处理来自框架QQ3076823485的消息

    @private_msg_handler(regexp=r'\\\[pic,[^]]+\\\]') #处理消息内容中含图片代码的消息

    @private_msg_handler(function=lambda x:x.msg.type=xlz.types.MessageTypes.好友消息.value) #处理好友私聊消息

    tip：三个参数可以同时使用，当同时满足所有条件时才会投递消息

    返回 True 拦截其他处理函数继续处理该消息
    """

    def decorator(
            func  # type: typing.Callable[[types.PrivateMsg], typing.Optional[bool]]
    ):
        @wraps(func)
        def wrapper():
            _private_handlers.append({'handler': func, 'bots': bots, 'regexp': regexp, 'function': function})
            logger.info(f'[{_get_stack()}]已设置一个私聊消息处理函数')
            return None

        return wrapper()

    return decorator


def group_msg_handler(
        bots=None,  # type: typing.Optional[list[int]]
        regexp=None,  # type: typing.Union[None, str, re.Pattern]
        function=None  # type: typing.Optional[typing.Callable[[types.GroupMsg], bool]]
):
    """
    群聊&讨论组消息处理 函数装饰器

    示例：

    @group_msg_handler(bots=[3076823485]) #处理来自框架QQ3076823485的消息

    @group_msg_handler(regexp=r'\\\[pic,[^]]+\\\]') #处理消息内容中含图片代码的消息

    @group_msg_handler(function=lambda x:x.msg.type=xlz.types.MessageTypes.讨论组消息.value) #处理讨论组消息

    tip：三个参数可以同时使用，当同时满足所有条件时才会投递消息

    返回 True 拦截其他处理函数继续处理该消息
    """

    def decorator(
            func  # type: typing.Callable[[types.GroupMsg], typing.Optional[bool]]
    ):
        @wraps(func)
        def wrapper():
            _group_handlers.append({'handler': func, 'bots': bots, 'regexp': regexp, 'function': function})
            logger.info(f'[{_get_stack()}]已设置一个群聊消息处理函数')
            return None

        return wrapper()

    return decorator


def event_msg_handler(
        bots=None,  # type: typing.Optional[list[int]]
        regexp=None,  # type: typing.Union[None, str, re.Pattern]
        function=None  # type: typing.Optional[typing.Callable[[types.EventMsg], bool]]
):
    """
    事件消息处理 函数装饰器

    示例：

    @event_msg_handler(bots=[3076823485]) #处理来自框架QQ3076823485的消息

    @event_msg_handler(regexp=r'\\\[pic,[^]]+\\\]') #处理消息内容中含图片代码的消息

    @event_msg_handler(function=lambda x:x.msg.type=xlz.types.EventTypes.群事件_某人撤回事件.value) #处理群聊撤回事件

    tip：三个参数可以同时使用，当同时满足所有条件时才会投递消息

    返回 True 拦截其他处理函数继续处理该消息
    """

    def decorator(
            func  # type: typing.Callable[[types.EventMsg], typing.Optional[bool]]
    ):
        @wraps(func)
        def wrapper():
            _event_handlers.append({'handler': func, 'bots': bots, 'regexp': regexp, 'function': function})
            logger.info(f'[{_get_stack()}]已设置一个事件消息处理函数')
            return None

        return wrapper()

    return decorator


def schedule_work_handler(
        arg=None  # type: typing.Optional[str]
):
    """
    定时任务处理 函数装饰器

    示例：

    @schedule_work_handler(arg='work') #处理参数为work的定时任务

    返回 True 拦截其他处理函数继续处理该消息
    """

    def decorator(
            func  # type: typing.Callable[[types.ScheduleWork], typing.Optional[bool]]
    ):
        @wraps(func)
        def wrapper():
            _event_handlers.append({'handler': func, 'arg': arg})
            logger.info(f'[{_get_stack()}]已设置一个定时任务处理函数')
            return None

        return wrapper()

    return decorator
