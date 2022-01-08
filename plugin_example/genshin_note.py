"""
ctrl+c ctrl+v 能用就行(
https://github.com/yaomeng0722/genshin_task-resin-expedition_alert
"""
import hashlib
import json
import os
import random
import re
import time
from typing import Any, List, Literal, Optional

import pydantic
import requests

import py_xlz_http as xlz

bind_cmd = r'绑定 ?([1256][0-9]{8}) (.*)'
avatar_json = {
    "Albedo": "阿贝多",
    "Ambor": "安柏",
    "Barbara": "芭芭拉",
    "Beidou": "北斗",
    "Bennett": "班尼特",
    "Chongyun": "重云",
    "Diluc": "迪卢克",
    "Diona": "迪奥娜",
    "Eula": "优菈",
    "Fischl": "菲谢尔",
    "Ganyu": "甘雨",
    "Hutao": "胡桃",
    "Jean": "琴",
    "Kazuha": "枫原万叶",
    "Kaeya": "凯亚",
    "Ayaka": "神里绫华",
    "Keqing": "刻晴",
    "Klee": "可莉",
    "Lisa": "丽莎",
    "Mona": "莫娜",
    "Ningguang": "凝光",
    "Noelle": "诺艾尔",
    "Qiqi": "七七",
    "Razor": "雷泽",
    "Rosaria": "罗莎莉亚",
    "Sucrose": "砂糖",
    "Tartaglia": "达达利亚",
    "Venti": "温迪",
    "Xiangling": "香菱",
    "Xiao": "魈",
    "Xingqiu": "行秋",
    "Xinyan": "辛焱",
    "Yanfei": "烟绯",
    "Zhongli": "钟离",
    "Yoimiya": "宵宫",
    "Sayu": "早柚",
    "Shogun": "雷电将军",
    "Aloy": "埃洛伊",
    "Sara": "九条裟罗",
    "Kokomi": "珊瑚宫心海"
}


class APIError(ValueError):
    def __init__(self, retcode: int, message: str) -> None:
        self.retcode: int = retcode
        self.message: str = message

    def __str__(self) -> str:
        return f"{self.retcode}: {self.message}"


class Response(pydantic.BaseModel):
    retcode: int
    message: str
    data: Optional[dict]


class BaseData(pydantic.BaseModel):
    """
    current_resin=35 当前树脂
    max_resin=160 树脂上限
    resin_recovery_time=59900 树脂恢复时间
    remain_resin_discount_num=3 本周剩余树脂减半次数
    resin_discount_num_limit=3 本周树脂减半次数上限

    current_expedition_num=5 当前派遣数量
    max_expedition_num=5 最大派遣数量
    finished_task_num=0 完成的委托数量
    total_task_num=4 全部委托数量
    is_extra_task_reward_received=False 每日委托奖励是否领取

    """
    current_resin: int
    max_resin: int
    resin_recovery_time: int
    remain_resin_discount_num: Literal[0, 1, 2, 3]
    resin_discount_num_limit: int = 3
    current_expedition_num: Literal[0, 1, 2, 3, 4, 5]
    max_expedition_num: Literal[0, 1, 2, 3, 4, 5]
    finished_task_num: Literal[0, 1, 2, 3, 4]
    total_task_num: int = 4
    is_extra_task_reward_received: bool
    current_home_coin: int
    max_home_coin: int
    home_coin_recovery_time: str

    expeditions: List[dict]


def get_server(uid: int) -> str:
    if str(uid).startswith('1'):
        return 'cn_gf01'  # 天空岛
    elif str(uid).startswith('5'):
        return 'cn_qd01'  # 世界树
    else:
        return ''


class Headers:
    def __init__(self) -> None:
        pass

    @staticmethod
    def md5(text: str) -> str:
        md5 = hashlib.md5()
        md5.update(text.encode())
        return md5.hexdigest()

    def create_dynamic_secret(self, query: dict, body: str) -> str:
        parameters: List[str] = [
            f'{k}={query[k]}' for k in sorted(query.keys())]
        q = '&'.join(parameters)

        salt: str = 'xV8v4Qu54lUKrEYFZkJhB8cuOh9Asafs'
        time_: str = str(int(time.time()))
        random_ = str(random.randint(100000, 199999))

        check: str = self.md5(
            f"salt={salt}&t={time_}&r={random_}&b={body}&q={q}")

        return ','.join((time_, random_, check))

    def new(self, cookie: str, query: dict, body: str = '') -> dict:
        ds = self.create_dynamic_secret(query, body)
        version: str = '2.11.1'
        return {
            'Accept': 'application/json, text/plain, */*',
            'DS': ds,
            'Origin': 'https://webstatic.mihoyo.com',
            'x-rpc-app_version': version,
            'User-Agent': f'Mozilla/5.0 (Linux; Android 6.0.1; MuMu Build/V417IR; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/68.0.3440.70 Mobile Safari/537.36 miHoYoBBS/{version}',
            'x-rpc-client_type': '5',
            'cookie': cookie,
            'Referer': 'https://webstatic.mihoyo.com/app/community-game-records/index.html?v=6',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,en-US;q=0.8',
            'X-Requested-With': 'com.mihoyo.hyperion'
        }


class MysAPI:

    def __init__(self, role_id: int, cookie: str):
        """

        :param role_id: avatar uid
        """
        self.server: str = get_server(role_id)
        self.role_id: int = role_id
        self.body: dict = {
            'server': self.server,
            'role_id': role_id
        }
        self.cookie: str = cookie

    @staticmethod
    def _request(url: str, cookie: str, method: Literal['GET', 'POST'] = 'GET', **kwargs: Any) -> dict:
        session = requests.session()
        query: dict = kwargs.get('params', {})
        body = kwargs.get('data', '')
        response = session.request(method, url, headers=Headers().new(
            cookie, query, body), **kwargs).json()
        response = Response.parse_obj(response)
        if response.retcode == 0:
            pass
        elif response.retcode == -10001:  # ds error
            raise RuntimeError(response.message)
        else:
            raise APIError(response.retcode, response.message)
        return response.data

    def get_dailyNote(self) -> BaseData:
        url = 'https://api-takumi.mihoyo.com/game_record/app/genshin/api/dailyNote'
        return_data = self._request(url, params=self.body, cookie=self.cookie)
        # print(return_data)
        return BaseData.parse_obj(return_data)


def seconds2hours(seconds: int) -> str:
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    return "%02d:%02d:%02d" % (h, m, s)


def get_resin_data(base_data: BaseData) -> str:
    current_resin: str = f"{base_data.current_resin}/{base_data.max_resin}"
    resin_data = f"当前树脂：{current_resin}"
    if base_data.current_resin < 160:
        resin_recovery_time = seconds2hours(base_data.resin_recovery_time)
        next_resin_rec_time = seconds2hours(
            8 * 60 - ((base_data.max_resin - base_data.current_resin) * 8 * 60 - base_data.resin_recovery_time))
        resin_data += f"\n下个/全部树脂恢复时间：{next_resin_rec_time}/{resin_recovery_time}"
    return resin_data


def get_resin_discount_data(base_data: BaseData) -> str:
    return f"周本树脂减半次数剩余：{base_data.remain_resin_discount_num}/{base_data.resin_discount_num_limit}"


def get_task_num_data(base_data: BaseData) -> str:
    return (f"今日完成委托数量：{base_data.finished_task_num}/{base_data.total_task_num} "
            f"奖励{'已' if base_data.is_extra_task_reward_received else '未'}领取")


def get_coin_data(base_data: BaseData) -> str:
    coin = f'{base_data.current_home_coin}/{base_data.max_home_coin}'
    if base_data.current_home_coin<base_data.max_home_coin:
        coin_rec_time=seconds2hours(int(base_data.home_coin_recovery_time))
        coin_add_speed=math.ceil((base_data.max_home_coin-base_data.current_home_coin)/(int(base_data.home_coin_recovery_time)/60/60))
        coin+=f'（{coin_rec_time} 约{coin_add_speed}/h）'
    return coin


def get_expedition_data(base_data: BaseData) -> str:
    expedition_info: list[str] = []
    finished = 0
    for expedition in base_data.expeditions:
        avatar: str = expedition['avatar_side_icon'][89:-4]
        try:
            avatar_name: str = avatar_json[avatar]
        except KeyError:
            avatar_name: str = avatar

        if expedition['status'] == 'Finished':
            expedition_info.append(f"{avatar_name} 探索完成")
            finished += 1
        else:
            remained_timed: str = seconds2hours(
                expedition['remained_time'])
            expedition_info.append(
                f"{avatar_name} 剩余时间{remained_timed}")

    expedition_data: str = "\n".join(expedition_info)
    return (f"当前探索派遣总数/完成/上限：{base_data.current_expedition_num}/{finished}/{base_data.max_expedition_num}\n"
            f"详细信息：\n{expedition_data}")


def bind(qq, uid, cookie):
    try:
        if not os.path.exists('data'):
            os.mkdir('data')
        if os.path.exists('data/genshin.json'):
            with open('data/genshin.json', encoding='utf-8') as f:
                j = json.load(f)
        else:
            j = {}

        j[str(qq)] = {'uid': int(uid), 'cookies': cookie}
        with open('data/genshin.json', 'w', encoding='utf-8') as f:
            json.dump(j, f)
    except:
        return False
    return True


def query_note(qq):
    try:
        if not os.path.exists('data'):
            os.mkdir('data')
        if os.path.exists('data/genshin.json'):
            with open('data/genshin.json', encoding='utf-8') as f:
                j = json.load(f)
        else:
            j = {}

        u = j.get(str(qq))
        if not u:
            return '请私聊绑定你的游戏UID与米游社cookies\n指令格式：绑定 游戏UID 米游社cookies\n米游社cookies可以通过浏览器F12查看'
        note_data = MysAPI(u['uid'], u['cookies']).get_dailyNote()
        return ('*数据刷新可能存在一定延迟，请以当前游戏实际数据为准\n'
                f'{get_resin_data(note_data)}\n'
                f'{get_resin_discount_data(note_data)}\n'
                f'{get_task_num_data(note_data)}\n'
                f'{get_coin_data(note_data)}\n'
                f'{get_expedition_data(note_data)}')
    except Exception as a:
        return '查询失败！请检查cookies与游戏uid是否对应或是否已开启米游社实时便笺功能，如确认无误仍然不行请联系机器主人\n' + str(a)


@xlz.private_msg_handler()
def private(message: xlz.types.PrivateMsg):
    # 自己在其他设备向别人发送消息时：数据.来源事件QQ 为收信QQ   数据.来源事件QQ昵称 为收信QQ昵称
    # 分片消息也将传入插件，方便进行撤回消息，如果你不需要分片消息，可以过滤掉分片消息
    # 当你未使用框架发送过匿名消息时，其他设备发送匿名消息，数据.框架QQ匿名Id=0，此时，可以使用API【强制取自身匿名Id】解决问题
    # 返回 True 拦截其他处理函数继续处理该消息

    if not message.from_qq.qq == message.logon_qq:  # 过滤自己(包括其他设备)的消息，你也可以不过滤
        if message.msg.type == xlz.types.MessageTypes.临时会话.value:
            if message.msg.subtype_temp == xlz.types.MessageTypes.临时会话_群临时.value:
                if message.msg.text.strip().startswith('绑定'):
                    r = re.match(bind_cmd, message.msg.text.strip())
                    if r:
                        if bind(message.from_qq.qq, r.group(1).strip(), r.group(2).strip()):
                            xlz.api.send_group_temp_msg(
                                message.logon_qq, message.from_group.group, message.from_qq.qq,
                                '绑定游戏UID与米游社cookies成功')
                        else:
                            xlz.api.send_group_temp_msg(
                                message.logon_qq, message.from_group.group, message.from_qq.qq,
                                '绑定游戏UID与米游社cookies失败，请重试')
                    else:
                        xlz.api.send_group_temp_msg(
                            message.logon_qq, message.from_group.group, message.from_qq.qq, '指令格式错误')

                if message.msg.text.strip() == '实时便笺':
                    xlz.api.send_group_temp_msg(
                        message.logon_qq, message.from_group.group, message.from_qq.qq, query_note(message.from_qq.qq))

        elif message.msg.type == xlz.types.MessageTypes.好友消息.value:
            # 在付费版本当中，真正的红包等将传入文本代码，直接发送红包等的代码将被框架转义，再传入，所以不用担心安全问题
            # 需要注意的是，当框架QQ未实名认证时，转账无法自动到账，将是这样的：[transfer,title=请点击收款,memo=QQ转账,transId=101000026901302104201398395831]
            # 所以当 title = 请点击收款 时，请注意，此时转账并未到账
            if message.msg.text.strip().startswith('绑定'):
                r = re.match(bind_cmd, message.msg.text.strip())
                if r:
                    if bind(message.from_qq.qq, r.group(1).strip(), r.group(2).strip()):
                        xlz.api.send_private_msg(
                            message.logon_qq, message.from_qq.qq, '绑定游戏UID与米游社cookies成功')
                    else:
                        xlz.api.send_private_msg(
                            message.logon_qq, message.from_qq.qq, '绑定游戏UID与米游社cookies失败，请重试')
                else:
                    xlz.api.send_private_msg(
                        message.logon_qq, message.from_qq.qq, '指令格式错误')

            if message.msg.text.strip() == '实时便笺':
                xlz.api.send_private_msg(
                    message.logon_qq, message.from_qq.qq, query_note(message.from_qq.qq))


@xlz.group_msg_handler()
def group(message: xlz.types.GroupMsg):
    # 分片消息也将传入插件，方便进行撤回消息，如果你不需要分片消息，可以过滤掉分片消息
    # 当你的插件需要弹框时，请在信息框标题注明这个弹框来自于哪个插件，以免对用户造成困扰
    # 当你未使用框架发送过匿名消息时，其他设备发送匿名消息，数据.框架QQ匿名Id=0，此时，可以使用API【强制取自身匿名Id】解决问题
    # 返回 True 拦截其他处理函数继续处理该消息

    # 过滤自己(包括其他设备)的消息，你也可以不过滤
    if message.from_qq.qq != message.logon_qq and message.from_qq.qq != message.logon_qq_anonymous_id:
        # 在付费版本当中，真正的红包等将传入文本代码，直接发送红包等的代码将被框架转义，再传入，所以不用担心安全问题

        if message.msg.subtype == xlz.types.MessageTypes.讨论组消息.value:
            # 讨论组消息处理
            pass

        else:
            if message.msg.text.strip() == '实时便笺':
                xlz.api.send_group_msg(
                    message.logon_qq, message.from_group.group,
                    xlz.utils.TextCode.at(message.from_qq.qq) + '\n' + query_note(message.from_qq.qq))


# 测试
if __name__ == '__main__':
    with open('cookies.txt', encoding='utf-8') as fn:
        cookies = fn.read()
    data = MysAPI(158408572, cookies).get_dailyNote()
    print(get_resin_data(data))
    print(get_resin_discount_data(data))
    print(get_task_num_data(data))
    print(get_expedition_data(data))
