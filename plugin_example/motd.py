# coding=utf-8
__name__ = 'MC服务器信息查询'

import mcstatus as mc

import py_xlz_http as xlz


def del_escape(string: str):
    # 48-57(0-9),65-90(A-Z),97-122(a-z)
    for i in range(48, 57 + 1):
        string = string.replace(f'§{chr(i)}', '')
    for i in range(65, 90 + 1):
        string = string.replace(f'§{chr(i)}', '')
    for i in range(97, 122 + 1):
        string = string.replace(f'§{chr(i)}', '')
    return string


def motd(address: str, logon_qq, source, is_fri):
    def parse_desc(desc):
        if 'extra' in desc:
            return ''.join([x['text'] for x in desc['extra']])
        if 'text' in desc:
            return desc['text']
        return desc

    address = address.strip()
    if not address:
        return ('[MCJE服务器信息]\n'
                '正确用法:\n'
                '!motd <服务器IP> (电脑版)\n'
                '!motdpe <服务器IP> (手机版)')

    try:
        ret = mc.MinecraftServer.lookup(address).status()
        latency = ret.latency
        ret = ret.raw
    except Exception as e:
        return f'[MCJE服务器信息]\n操作失败：{e}'

    pic_text = ''
    if 'favicon' in ret:
        pic_b64 = ret['favicon'].replace('data:image/png;base64,', '')
        if is_fri:
            pic_code = xlz.api.upload_friend_pic(logon_qq, source, pic_b64)
        else:
            pic_code = xlz.api.upload_group_pic(logon_qq, source, pic_b64)
        pic_text = f'显示图标：{pic_code}\n'

    players = ''
    if 'sample' in ret['players']:
        player_list = [del_escape(x["name"]) for x in ret["players"]["sample"]]
        player_list = [x for x in player_list if x]
        players = f'玩家列表（最多显示十个）：{", ".join(player_list[:10])}\n'

    mod_info = ''
    if 'modinfo' in ret:
        if ret["modinfo"]["modList"]:
            mod_info = '\n' + '\n'.join([f'{x["modid"]} - {x["version"]}' for x in ret["modinfo"]["modList"]][:10])
        else:
            mod_info = '无'
        mod_info = f'\nMod端类型：{ret["modinfo"]["type"]}\nMod列表（最多显示十个）：{mod_info}'

    players_online = ret["players"]["online"]
    players_max = ret["players"]["max"]
    online_percent = round(players_online / players_max * 100, 2)

    return ('[MCJE服务器信息]\n'
            f'{pic_text}'
            f'服务端名：{ret["version"]["name"]}\n'
            f'协议版本：{ret["version"]["protocol"]}\n'
            f'当前人数：{players_online}/{players_max}({online_percent}%)\n'
            f'{players}'
            f'描述文本：\n{del_escape(parse_desc(ret["description"]))}\n'
            f'游戏延迟：{latency}ms'
            f'{mod_info}')


def motdpe(address: str):
    address = address.strip()
    if not address:
        return ('[MCBE服务器信息]\n'
                '正确用法:\n'
                '!motd <服务器IP> (电脑版)\n'
                '!motdpe <服务器IP> (手机版)')

    try:
        ret = mc.MinecraftBedrockServer.lookup(address).status()
    except Exception as e:
        return f'[MCBE服务器信息]\n操作失败：{e}'

    map_name = f'存档名称：{del_escape(ret.map)}\n' if ret.map else ''
    game_mode = f'游戏模式：{ret.gamemode}\n' if ret.gamemode else ''
    online_percent = round(int(ret.players_online) / int(ret.players_max) * 100, 2)

    return ('[MCBE服务器信息]\n'
            f'协议版本：{ret.version.protocol}\n'
            f'游戏版本：{ret.version.version}\n'
            f'描述文本：{del_escape(ret.motd)}\n'
            f'在线人数：{ret.players_online}/{ret.players_max}({online_percent}%)\n'
            f'{map_name}'
            f'{game_mode}'
            f'游戏延迟：{round(ret.latency * 1000, 3)}ms')


@xlz.private_msg_handler()
def private(message: xlz.types.PrivateMsg):
    # 自己在其他设备向别人发送消息时：数据.来源事件QQ 为收信QQ   数据.来源事件QQ昵称 为收信QQ昵称
    # 分片消息也将传入插件，方便进行撤回消息，如果你不需要分片消息，可以过滤掉分片消息
    # 当你未使用框架发送过匿名消息时，其他设备发送匿名消息，数据.框架QQ匿名Id=0，此时，可以使用API【强制取自身匿名Id】解决问题
    # 返回 True 拦截其他处理函数继续处理该消息

    if not message.from_qq.qq == message.logon_qq:  # 过滤自己(包括其他设备)的消息，你也可以不过滤
        text = message.msg.text.strip()

        if message.msg.type == xlz.types.MessageTypes.临时会话.value:

            if message.msg.subtype_temp == xlz.types.MessageTypes.临时会话_群临时.value:
                if text.startswith('!motdpe'):
                    content = motdpe(text[7:])
                    xlz.api.send_group_temp_msg(message.logon_qq, message.from_group.group,
                                                message.from_qq.qq, content)
                    return True

                if text.startswith('!motd'):
                    content = motd(text[5:], message.logon_qq, message.from_group.group, False)
                    xlz.api.send_group_temp_msg(message.logon_qq, message.from_group.group,
                                                message.from_qq.qq, content)
                    return True

            elif message.msg.subtype_temp == xlz.types.MessageTypes.临时会话_讨论组临时.value:
                if text.startswith('!motdpe'):
                    content = motdpe(text[7:])
                    xlz.api.send_discussion_temp_msg(message.logon_qq, message.from_group.group,
                                                     message.from_qq.qq, content)
                    return True

                if text.startswith('!motd'):
                    content = motd(text[5:], message.logon_qq, message.from_group.group, False)
                    xlz.api.send_discussion_temp_msg(message.logon_qq, message.from_group.group,
                                                     message.from_qq.qq, content)
                    return True

        elif message.msg.type == xlz.types.MessageTypes.好友消息.value:
            # 在付费版本当中，真正的红包等将传入文本代码，直接发送红包等的代码将被框架转义，再传入，所以不用担心安全问题
            # 需要注意的是，当框架QQ未实名认证时，转账无法自动到账，将是这样的：[transfer,title=请点击收款,memo=QQ转账,transId=101000026901302104201398395831]
            # 所以当 title = 请点击收款 时，请注意，此时转账并未到账

            if text.startswith('!motdpe'):
                content = motdpe(text[7:])
                xlz.api.send_private_msg(message.logon_qq, message.from_qq.qq, content)
                return True

            if text.startswith('!motd'):
                content = motd(text[5:], message.logon_qq, message.from_group.group, True)
                xlz.api.send_private_msg(message.logon_qq, message.from_qq.qq, content)
                return True


@xlz.group_msg_handler()
def group(message: xlz.types.GroupMsg):
    # 分片消息也将传入插件，方便进行撤回消息，如果你不需要分片消息，可以过滤掉分片消息
    # 当你的插件需要弹框时，请在信息框标题注明这个弹框来自于哪个插件，以免对用户造成困扰
    # 当你未使用框架发送过匿名消息时，其他设备发送匿名消息，数据.框架QQ匿名Id=0，此时，可以使用API【强制取自身匿名Id】解决问题
    # 返回 True 拦截其他处理函数继续处理该消息

    if message.from_qq.qq != message.logon_qq and message.from_qq.qq != message.logon_qq_anonymous_id:  # 过滤自己(包括其他设备)的消息，你也可以不过滤
        # 在付费版本当中，真正的红包等将传入文本代码，直接发送红包等的代码将被框架转义，再传入，所以不用担心安全问题

        text = message.msg.text.strip()
        reply_content = xlz.utils.TextCode.reply(
            message.msg.text, message.from_qq.qq, message.timestamp.recv, message.msg.req, message.msg.random)

        if text.startswith('!motdpe'):
            content = reply_content + motdpe(text[7:])

            if message.msg.subtype == xlz.types.MessageTypes.讨论组消息.value:
                xlz.api.send_discussion_msg(message.logon_qq, message.from_group.group, content)
            else:
                xlz.api.send_group_msg(message.logon_qq, message.from_group.group, content)

            return True

        if text.startswith('!motd'):
            content = reply_content + motd(text[5:], message.logon_qq, message.from_group.group, False)

            if message.msg.subtype == xlz.types.MessageTypes.讨论组消息.value:
                xlz.api.send_discussion_msg(message.logon_qq, message.from_group.group, content)
            else:
                xlz.api.send_group_msg(message.logon_qq, message.from_group.group, content)

            return True


xlz.logger.info(f'示例插件[{__name__}]加载完毕，作者：student_2333，GitHub：https://github.com/lgc2333/py-xlz-http-v2')
