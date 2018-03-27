import json
import logging
from configparser import ConfigParser

import requests

logger = logging.getLogger(__name__)


class TulingBot:
    """A simple tuning bot api

    http://www.tuling123.com

    by Wenoptk
    """
    APIURL = 'http://www.tuling123.com/openapi/api'
    def __init__(self, apikey: str):
        self.apikey = apikey

    @staticmethod
    def _parse_response(content: bytes):
        if not content:
            return None
        c = content.decode()
        return json.loads(c)

    def send(self, msg: str, userid: str) -> str:
        j = {
            "key": self.apikey,
            "info": msg,
            "userid": userid
        }
        try:
            ret = requests.post(self.APIURL, json=j)
            ret = self._parse_response(ret.content)
            if not ret:
                return ''
            if ret.get('code') == 40004:
                logger.info('40004: 当天请求次数已使用完')
            return ret.get('text')
        except:
            logger.error('error in send message.', exc_info=True)
            return ''


if __name__ == '__main__':
    c = ConfigParser()
    c.read_file(open('F:/Workplace-P2/cr-bot/_configs/private.ini', 'r', encoding='utf-8'))
    key = c.get('tulingbot', 'key')
    assert key is not None

    t = TulingBot(key)
    r = t.send('你好', 'id0000')
    if r:
        print(r)