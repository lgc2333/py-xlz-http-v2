# coding=utf-8
"""
py-xlz-http  version 2.0.3(20210724)

Copyright (c) 2021 student_2333

License: LGPL-2.1

----

作者的话

非常感谢大家的支持与厚爱！花了一些时间重写了这个项目，希望大家喜欢！

欢迎大家踊跃参与本项目的开发！我一个人开发此项目难免有些疏漏，可以积极发issue、提交pull request哦！感谢大家帮助完善这个项目！

觉得项目不错的话，就请赏个star吧！另外，赞助作者请加QQ群！公告有付款码～

----

联系方式

QQ:3076823485

QQ Group:1105946125

E-mail:lgc2333@126.com

Telegram:@lgc2333
"""
__version__ = "2.0.3(20210724)"

import time

print(__doc__.replace('\n\n', '\n').strip())

# ====== 供外部调用
import py_xlz_http.api
import py_xlz_http.types
import py_xlz_http.utils
from py_xlz_http.main import *


# ====== 检查更新
def _check_version():
    while True:
        logger.info('正在检查本包更新')
        import requests
        try:
            ret = requests.get(
                'http://lgc2333.top:88/pl_get',
                params={'type': 'py', 'name': 'httpv2'}
            ).json()
        except:
            logger.error(f'检查本包更新失败：请求接口失败：\n{traceback.format_exc()}')
        else:
            if ret['ok']:
                result = ret['result']
                if result["version"] == __version__:
                    logger.info(f'检查本包更新成功：当前为最新版本{__version__}')
                else:
                    logger.info(f'检查本包更新成功：需要更新\n'
                                f'当前版本：{__version__}，最新版本：{result["version"]}\n'
                                f'更新说明：{result["description"]}\n'
                                f'下载链接：{result["down_link"]}')
            else:
                logger.warning(f'请求接口出错：\n{ret["result"]}')
        time.sleep(10 * 60)


t = threading.Thread(target=_check_version)
t.setDaemon(True)
t.start()
