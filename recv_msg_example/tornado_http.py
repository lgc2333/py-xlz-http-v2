# coding=utf-8
"""
简易tornado搭建HTTP服务器webhook收消息示例
"""
import os
import pkgutil
import sys
import time
import traceback

from tornado import web, httpserver, ioloop

import py_xlz_http as xlz

port = 6677  # 服务器端口


class Main(web.RequestHandler):
    """数据接收"""

    def get(self):
        self.write('<center><h1>如果你能看到这个，就证明服务器启动成功啦！</h1></center>')

    def post(self):
        data = self.request.body.decode('utf-8')
        xlz.logger.debug('收到数据：' + data)
        xlz.update_msg(data)


if __name__ == '__main__':
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

    # 启动服务器
    xlz.logger.info('服务器启动中')
    svr = httpserver.HTTPServer(
        web.Application([('/', Main)])
    )
    svr.bind(port)
    svr.start()
    xlz.logger.info(f'服务器启动成功，端口{port}')
    try:
        ioloop.IOLoop.current().start()
    except:
        xlz.logger.error(f'发生未处理异常：\n{traceback.format_exc()}')
        input('按回车键退出...')
