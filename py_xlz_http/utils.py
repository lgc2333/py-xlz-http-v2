# coding=utf-8
"""实用功能函数"""
import json
import re


def usc2_to_unicode(usc2_str: str) -> str:
    """将含有usc2文本的字符串转为unicode字符串"""
    for x in set([x[0] for x in re.findall(r'((\\u([a-z0-9]|[A-Z0-9]){4})+)', usc2_str)]):  # 寻找\uxxxx
        usc2_str = usc2_str.replace(x, json.loads(f'{{"a":"{x}"}}')['a'])
        # 为什么不用str.decode('unicode-escape')？因为json模块解析能处理emoji等特殊utf-16字符
    return usc2_str


def unicode_to_usc2(unicode_str: str, escape=True) -> str:
    """字符串usc2编码"""
    strings = unicode_str.split('\n')  # 分开处理以解决换行符问题，不能用splitlines因为会去掉末尾单个换行符
    # print(strings)
    decoded_str = []
    for string in strings:
        txt = json.dumps({'a': string})  # 为什么不用str.encode('unicode-escape')？因为json文本好处理反斜杠转义
        txt = txt[txt.find(': "') + 3:txt.rfind('"')]  # 取出{"a": "xxx"}中的xxx
        decoded_str.append(txt.replace('\\\\', '\\u005c'). \
                           replace('[', '\\u005b'). \
                           replace(']', '\\u005d') if escape else txt)  # 反斜杠，中括号转义
    return '\n'.join(decoded_str)


def escape_text(text: str) -> str:
    """将文本当中的[、]、\进行转义以防框架误识文本为文本代码"""
    return text.replace('\\', '\\u005c').replace('[', '\\u005b').replace(']', '\\u005d')


def unescape_text(text: str) -> str:
    """将经过转义的[、]、\反转义回来"""
    return text.replace('\\u005c', '\\').replace('\\u005b', '[').replace('\\u005d', ']') \
        .replace('\\u005C', '\\').replace('\\u005B', '[').replace('\\u005D', ']')


def over_len_int_to_long(num: int):
    """传入超长的整数，返回长整数，以此解决数值超出易语言整数型范围而显示为负数的问题

    用于解决消息数据的时间戳过大超出易语言整数类型范围而显示为负数的问题"""
    if num < 0:
        return num & 4294967295
    return num


def make_cookie(qq, skey, p_skey) -> str:
    """组cookie

    容易失效，建议还是使用client_key登录取cookie"""
    q = str(qq)
    a = len(q)
    if a < 10:
        q = '0' * (10 - a) + q  # qq补零
    return f'uin={q}; p_uin={q}; skey={skey}; p_skey={p_skey};'


def color_hex_to_int(hex_color: str) -> int:
    """十六进制颜色值转易语言十进制颜色值"""
    hex_color = hex_color.replace('#', '').lower()
    if len(hex_color) == 6 and hex_color.isalnum():
        try:
            int_color = int(hex_color, 16)
        except:
            raise ValueError(f'{hex_color} is not a hex color')
        else:
            return int_color
    raise ValueError(f'{hex_color} is not a hex color')


def color_rgb_to_int(r: int, g: int, b: int) -> int:
    """rgb颜色值转易语言十进制颜色值"""
    if not 0 <= r <= 255:
        raise ValueError('"r" should be 0<=r<=255')
    if not 0 <= g <= 255:
        raise ValueError('"g" should be 0<=g<=255')
    if not 0 <= b <= 255:
        raise ValueError('"b" should be 0<=b<=255')
    return int.from_bytes(bytes([r, g, b]), 'big')


class TextCode:
    @staticmethod
    def voice_local_path(file_path, voice_type=0, text='', length=0):
        """
        语音_本地

        :param file_path: 文件路径 必须是 silk_v3 或 amr 编码的文件
        :param voice_type: 语音类型 0普通语音,1变声语音,2文字语音,3红包匹配语音
        :param text: 语音文字 文字语音填附加文字(腾讯貌似会自动替换为语音对应的文本),匹配语音填a、b、s、ss、sss，注意是小写
        :param length: 时长
        :return:
        """
        return f'[AudioFile,path={file_path},type={voice_type},content=”{text},time={length}]'

    @staticmethod
    def yellow_face(face_id):
        """
        小黄豆表情

        :param face_id: id
        :return:
        """
        return f'[bq{face_id}]'

    @staticmethod
    def big_face(face_id, name, face_hash, flag):
        """
        大表情

        :param face_id: Id
        :param name: name
        :param face_hash: hash
        :param flag: flag
        :return:
        """
        return f'[bigFace,Id={face_id},name={name},hash={face_hash},flag={flag}]'

    @staticmethod
    def little_face(face_id, name):
        """
        小表情

        :param face_id: Id
        :param name: name
        :return:
        """
        return f'[smallFace,name={name},Id={face_id}]'

    @staticmethod
    def face(face_id, name):
        """
        表情

        :param face_id: id
        :param name: name
        :return:
        """
        return f'[Face,Id={face_id},name={name}]'

    @staticmethod
    def little_video(link_param, hash1, hash2, width=0, height=0, length=0):
        """
        小视频

        :param link_param: linkParam
        :param hash1: hash1
        :param hash2: hash2
        :param width: 宽度
        :param height: 高度
        :param length: 时长
        :return:
        """
        return (f'[litleVideo,linkParam={link_param},hash1={hash1},hash2={hash2},wide={width},high={height},'
                f'time={length}]')

    @staticmethod
    def at(qq, add_space=True):
        """
        艾特

        :param qq: 对方QQ
        :param add_space: 添加空格 true：添加 false：不添加 美化at显示效果
        :return:
        """
        return f'[@{qq}]' + ' ' if add_space else f'[@{qq}]'

    @staticmethod
    def at_all():
        """
        艾特全体（需要管理员）

        :return:
        """
        return '[@all]'

    @staticmethod
    def pic_local_path(path, width=0, height=0, flash=False):
        """
        图片_本地

        :param path: 文件路径
        :param width: 宽度，只影响ios
        :param height: 高度，只影响ios
        :param flash: 为true时自动播放动图
        :return:
        """
        return f'[picFile,path={path},wide={width},high={height},cartoon={str(flash).lower()}]'

    @staticmethod
    def flash_pic_local_path(path, width=0, height=0, flash=False):
        """
        闪照_本地

        :param path: 文件路径
        :param width: 宽度，只影响ios
        :param height: 高度，只影响ios
        :param flash: 为true时自动播放动图
        :return:
        """
        return f'[flashPicFile,path={path},wide={width},high={height},cartoon={str(flash).lower()}]'

    @staticmethod
    def shake(shake_id, shake_type, name):
        """
        抖一抖

        :param shake_id: Id
        :param shake_type: type
        :param name: name
        :return:
        """
        return f'[Shake,name={name},Type={shake_type},Id={shake_id}]'

    @staticmethod
    def limi_show(show_id, show_type, name, info):
        """
        厘米秀 厘米秀的info是json格式消息,可通过usc2_to_unicode解码文本代码里的info值得到

        :param show_id: Id
        :param show_type: Type
        :param name: name
        :param info: info json格式 厘米秀数据
        :return:
        """
        return f'[limiShow,Id={show_id},name={name},type={show_type},info={unicode_to_usc2(usc2_to_unicode(info))}]'

    @staticmethod
    def reply(msg, qq, recv_time, req, random):
        """
        回复消息

        :param msg: 对方发送内容
        :param qq: 对方QQ
        :param recv_time: 消息接收时间
        :param req: 消息req
        :param random: 消息random
        :return:
        """
        return (f'[Reply,Content={unicode_to_usc2(usc2_to_unicode(msg))},SendQQID={qq},Req={req},Random={random},'
                f'SendTime={recv_time}]')

    @staticmethod
    def flash_word(desc, res_id, prompt):
        """
        闪字

        :param desc: desc
        :param res_id: resid
        :param prompt: prompt 注意此处不支持其他文本代码
        :return:
        """
        return f'[flashWord,Desc={desc},Resid=”{res_id},Prompt={prompt}]'

    @staticmethod
    def honest(qq, nick, description, send_time, random, bg_type):
        """
        坦白说

        :param qq: 对方QQ 可自定义
        :param nick: 对方昵称 可自定义
        :param description: 描述 可自定义
        :param send_time: 发送时间 10位时间戳，可自定义
        :param random: 发送Random 可自定义
        :param bg_type: 背景类型 可自定义，不同背景对应的值日志查看
        :return:
        """
        return f'[Honest,ToUin={qq},ToNick={nick},Desc={description},Time={send_time},Random={random},Bgtype={bg_type}]'

    @staticmethod
    def graffiti(model_id, graffiti_hash, pic_url):
        """
        涂鸦 手画数据是[涂鸦hash]和[涂鸦图片地址]，背景是[模型Id]，可以自由组合数据和模型，比如你可以换掉别人涂鸦消息的模型(背景)

        :param model_id: 模型Id 手机QQ上涂鸦背景从左往右数，从0开始
        :param graffiti_hash: 涂鸦hash 和图片地址对应
        :param pic_url: 涂鸦图片地址 和hash对应
        :return:
        """
        return f'[Graffiti,ModelId={model_id},hash={graffiti_hash},url={pic_url}]'

    @staticmethod
    def show_pic(pic_hash, show_type=40000, width=0, height=0, flash=False):
        """
        秀图 秀图文本代码只支持群聊发送

        :param pic_hash: 图片hash 通过群图片代码获得
        :param show_type: 秀图类型 40000普通,40001幻影,40002抖动,40003生日,40004爱你,40005征友
        :param width: 宽度 只影响ios
        :param height: 高度 只影响ios
        :param flash: 动图 为true时可自动播放动图
        :return:
        """
        return f'[picShow,hash={pic_hash},showtype={show_type},wide={width},high={height},cartoon={str(flash).lower()}]'

    @staticmethod
    def dice(point=1):
        """
        随机骰子（小知识 tóu骰）

        :param point: 骰子点数 1-6,不在1-6的范围时,默认无结果(无限摇骰子)
        :return:
        """
        return (f'[bigFace,Id=11464,name=[随机骰子]{point if 1 <= point <= 6 else ""},'
                f'hash=4823D3ADB15DF08014CE5D6796B76EE1,flag=409e2a69b16918f9]')

    @staticmethod
    def stick_msg(x, y, width, height, rotate, recv_time, req, random):
        """
        粘贴消息 粘贴内容直接追加在文本代码后面,粘贴内容只支持图片、表情

        :param x: X值 与粘贴位置有关,由横向位置经过特定算法得到
        :param y: Y值 与粘贴位置有关,由纵向位置经过特定算法得到
        :param width: 粘贴内容宽值 可决定粘贴内容的宽度,由缩放宽度经过特定算法得到
        :param height: 粘贴内容高值 可决定粘贴内容的高度,由缩放高度经过特定算法得到
        :param rotate: 粘贴倾角 粘贴内容与水平位置的倾角
        :param recv_time: 消息接收时间
        :param req: 消息req
        :param random: 消息random
        :return:
        """
        return (f'[Sticker,X={x},Y={y},Width={width},Height={height},Rotate={rotate},Req={req},Random={random},'
                f'SendTime={recv_time}]')

    @staticmethod
    def mora(gesture):
        """
        自定义猜拳

        :param gesture: 类型 1-3,1石头,2剪刀,3布,不在1-3的范围时,默认无结果(无限改变猜拳结果)
        :return:
        """
        return (f'[bigFace,Id=11415,name=[猜拳]{gesture if 1 <= gesture <= 3 else ""},'
                f'hash=83C8A293AE65CA140F348120A77448EE,flag=7de39febcf45e6db]')

    @staticmethod
    def share_card(acc, share_type=0):
        """
        分享名片 名片分享

        :param acc: 分享账号 Type为0则表示QQ号,Type为其他则表示群号
        :param share_type: Type 0为群分享,其他则为好友分享
        :return:
        """
        return f'[Share,ID={acc},Type={"Group" if share_type == 0 else "Friend"}]'
