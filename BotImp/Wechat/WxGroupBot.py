import inspect
import logging

from BotImp.cmdpattern import hashtag_cmd_parse
from ChatBot.CommandBot import CommandBot
from ChatBot.PublishBot import PublishBot
from pyWechatProxyClient.Client import Client
from pyWechatProxyClient.api.consts import TEXT
from pyWechatProxyClient.api.model.Chat import Chat
from pyWechatProxyClient.api.model.Friend import Friend
from pyWechatProxyClient.api.model.Group import Group
from pyWechatProxyClient.api.model.Message import Message
from Utils.util import is_wordlist_in_txt

logger = logging.getLogger(__name__)


class WechatBot(CommandBot, PublishBot):

    # ---------------- CommandBot Overrides ---------------
    def _callback_on_non_command_msg(self, msg, from_who, reply, *a, **ka):
        re_msg = ''
        if is_wordlist_in_txt(['帮助', '怎么用', 'help', '#'], msg):
            re_msg = '支持命令:"{}", 在命令前加#以使用'.format(
                '", "'.join(self.list_supported_command)
            )

        elif ka.get('from_group'):
            # if self.tulingbot:
            #     re_msg = self.tulingbot.send(msg)
            pass

        from_who.send(re_msg)

    def _callback_on_command_not_supported(self, command, msg, from_who, reply, *a, **ka):
        from_who.send("命令未识别")
        re_msg = '支持命令:"{}", 在命令前加#以使用'.format(
            '", "'.join(self.list_supported_command)
        )
        from_who.send(re_msg)

    def _command_extractor(self, msg) -> (str, str):
        """Command parser for CommandBot command"""
        return hashtag_cmd_parse(msg)

    # ---------------- PublishBot Overrides ---------------

    def push_message_to(self, msg, to_whom):
        assert isinstance(to_whom, Chat)
        to_whom.send(msg)

    def publish_message(self, msg):
        """
        Send message to group
        :param msg:
        :return:
        """
        logger.info("sending msg to group: %s", msg)
        self.wx_group.send(msg)
    # -----------------------------------------------------

    def __init__(self, id_group, id_op, wxproxy_server_url, tulingbot=None):
        super().__init__()
        self.wxproxy_server_url = wxproxy_server_url
        self.tulingbot = tulingbot
        self.__group_wx_id = id_group
        self.__op_wx_id = id_op
        if not id_group:
            logger.warning('group id is "{}"'.format(id_group))
        if not id_op:
            logger.warning('op id is "{}"'.format(id_op))

        self.__on_group_msg_handler = None

        self.wxproxy_client = None
        self.wx_group = None
        self.wx_op = None

        self.setup_wechat()
        logger.info('WechatBot initialized.')

    def setup_wechat(self):
        """Setup WechatProxy"""
        self.wxproxy_client = Client(self.wxproxy_server_url)
        self.wxproxy_client.start()
        self.register_wechat_components()

    def register_wechat_components(self):
        self.wx_op = Friend(friend_id=self.__op_wx_id)
        self.wx_op.client = self.wxproxy_client
        self.wx_group = Group(group_chat_id=self.__group_wx_id)
        self.wx_group.client = self.wxproxy_client

        self._register_msg_handler()
        self.set_op(self.wx_op)

    def startup_welcome(self, msg='Hi, I am coming'):
        self.wx_op.send(msg)

    def set_on_group_message_callback(self, handler):
        """

        :param handler:
            yourCallback(message, group_chat, reply_handler)
        :return:
        """
        if not inspect.isfunction(handler):
            raise ValueError('handler is not function')
        self.__on_group_msg_handler = handler

    def set_on_wechat_system_message_callback(self, handler):
        """

        :param handler:
            yourCallback(message, chat, reply_handler)
        :return:
        """
        if not inspect.isfunction(handler):
            raise ValueError('handler is not function')

        def on_system_msg(_, msg):
            handler.__call__(msg, msg.sender, msg.sender.send)

        self.wxproxy_client.set_system_message_handler(on_system_msg)

    def send_text_to_group(self, msg):
        self.publish_message(msg)

    send_to_group = send_text_to_group

    def _register_msg_handler(self):

        @self.wxproxy_client.register(self.wx_group)
        def __on_group_msg(msg: Message):
            """Handler for message received from group"""
            # logger.debug('receive from group chat: from %s, says:"%s"', msg.member, msg.text)
            if msg.type == TEXT:
                # Only process command message with TEXT message
                is_op = msg.member == self.wx_op
                try:
                    self._callme_to_process_command_message(msg.text, self.wx_group, self.wx_group.send,
                                                            from_group=True, talker_in_group=msg.member, is_op=is_op)
                except:
                    logger.error('error occur in "_callme_to_process_command_message"',
                                 exc_info=True)
                    self.wx_group.send('好像出了什么问题...')

            # Call the ambient handler
            if inspect.isfunction(self.__on_group_msg_handler):
                try:
                    self.__on_group_msg_handler.__call__(message=msg, chat=self.wx_group, reply=self.wx_group.send)
                except:
                    logger.error('error occur in "%s(...)"', self.__on_group_msg_handler.__name__,
                                 exc_info=True)

        @self.wxproxy_client.register(self.wx_op)
        def __on_op_msg(msg: Message):
            """Handler for when message received from Op"""
            if self.tulingbot:
                return self.tulingbot.send(msg.text, userid=self.wx_op.talker_id)
            else:
                return "ok"

    def reply_by_tuling(self, to: Chat, msg: str, userid, default=''):
        """Reply by tulingbot, if get message from tuling failed, use `default` """
        if not self.tulingbot:
            logger.warning('tuling-bot not init. did you enable it?')
            to.send(default)
            return
        r = self.tulingbot.send(msg, userid=userid)
        if not r:
            to.send(default)
            return
        to.send(r)

    def join_thread(self):
        self.wxproxy_client.join()

    def stop(self):
        self.wxproxy_client.stop()
