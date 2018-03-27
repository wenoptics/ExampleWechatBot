import re


def hashtag_cmd_parse(txt) -> (str, str):
    """
    定义以#开头的命令样式
    :param msg:
    :return:
    """
    try:
        match = re.search('#(\S+)\s*(.*)', txt)
        if match:
            return match.group(1), match.group(2)
    except:
        pass
    return None, None