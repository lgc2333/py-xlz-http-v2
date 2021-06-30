# coding=utf-8
"""
简易websocket连接收消息示例

bug一大堆，不知道是谁的锅
"""
import hashlib
import os
import pkgutil
import sys
import time
import traceback

import websocket

import py_xlz_http as xlz

max_reconnect_tries = 5  # 最大尝试重连总次数
heartbeat_interval = 5  # 心跳延时（秒），如果10秒钟无心跳包自动断连，我折中了，作者建议1秒一个包

tries = 0  # 重连总次数计数


def on_message(_, message):
    xlz.logger.debug('收到数据：' + message)
    xlz.update_msg(message)


def on_error(_, __):
    # xlz.logger.error(f'发生异常：{__}')
    xlz.logger.error(f'发生未处理异常：\n{traceback.format_exc()}')


def on_close(ws, code, msg):
    xlz.logger.info(f'连接被关闭([{code}]{msg})，尝试重连')
    reconnect(ws)


def reconnect(ws: websocket.WebSocketApp):
    global tries
    while True:
        if tries >= max_reconnect_tries:
            xlz.logger.info(f'已达到最大尝试重连总次数{max_reconnect_tries}')
            input('按回车键退出...')
            sys.exit()
        else:
            tries += 1
            xlz.logger.info(f'进行第{tries}次重连')
            ws.close()
            svr.run_forever(ping_interval=heartbeat_interval)


if __name__ == '__main__':
    def md5_encode(string: str):
        """字符串md5加密"""
        if string:
            m = hashlib.md5()
            m.update(string.encode('utf-8'))
            return m.hexdigest()
        return ''


    # 置API访问数据
    xlz.api.init('http://localhost:10429')

    # 加载插件
    xlz.logger.info('正在加载插件')
    if not os.path.exists('plugins'):
        os.mkdir('plugins')
    total = 0
    for finder, name, _ in pkgutil.walk_packages(["plugins"]):
        xlz.logger.info(f'正在加载插件 {name}')
        try:
            t = int(round(time.time() * 1000))  # 13位时间戳，计算用时
            module = finder.find_module(name).load_module(name)
        except Exception:
            xlz.logger.info(f'加载插件 {name} 失败\n{traceback.format_exc()}')
            try:
                del sys.modules[name]
            except:
                pass
        else:
            xlz.logger.info(f'加载插件 {name} 成功，用时{int(round(time.time() * 1000)) - t}ms')
            total += 1
    xlz.logger.info(f'插件加载完毕，共加载成功 {total} 个插件')

    # 远程连接时的身份验证，如不需要可以注释
    # '''
    user = 'user'  # 用户
    password = 'pass'  # 密码
    t = int(time.time())
    s = md5_encode(f'{user}/ws{md5_encode(password)}{t}')
    auth = f'?user=user&timestamp={t}&signature={s}'
    # '''
    # auth = ''

    svr = websocket.WebSocketApp(
        f'ws://localhost:10429/ws{auth}',
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
    )
    xlz.logger.info('尝试启动服务器')
    svr.run_forever(ping_interval=heartbeat_interval)
