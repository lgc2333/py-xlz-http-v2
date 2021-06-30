# coding=utf-8
"""
简易flask搭建HTTP服务器webhook收消息示例
"""
import os
import pkgutil
import sys
import time
import traceback

from flask import Flask, request

import py_xlz_http as xlz

port = 6677  # 服务器端口

app = Flask(__name__)


@app.route("/", methods=['GET'])
def get():
    return '<center><h1>如果你能看到这个，就证明服务器启动成功啦！</h1></center>'


@app.route("/", methods=['POST'])
def post():
    data = request.stream.read().decode('utf-8')
    xlz.logger.debug('收到数据：' + data)
    xlz.update_msg(data)
    return ''


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

    xlz.logger.info(f'尝试启动服务器，可以访问 http://localhost:{port}/ 查看是否启动成功')
    app.run(
        '0.0.0.0',
        port
    )
