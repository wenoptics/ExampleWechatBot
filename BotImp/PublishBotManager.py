import logging

from ChatBot.PublishBot import PublishBot

logger = logging.getLogger(__name__)


class PublishBotManager(PublishBot):
    def __init__(self):
        super().__init__()
        self._registered_bots = []

    def register(self, bot: PublishBot):
        if bot in self._registered_bots:
            logger.warning('bot `%s` already registered', bot)
            return
        if not isinstance(bot, PublishBot):
            raise ValueError
        self._registered_bots.append(bot)

    def push_message_to(self, msg, to_whom):
        raise RuntimeError('Should not call this method from {}'.format(self.__class__.__name__))

    def publish_message(self, msg):
        for bot in self._registered_bots:
            bot.publish_message(msg)
