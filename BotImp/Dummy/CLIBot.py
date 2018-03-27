import logging

from BotImp.cmdpattern import hashtag_cmd_parse
from ChatBot.CommandBot import CommandBot
from ChatBot.PublishBot import PublishBot


class CLIBot(CommandBot, PublishBot):
    def __init__(self):
        super().__init__()
        self.prompt = '(%s) ' % self.__class__.__name__
        self.printout_prefix = '|> '

    # Override for PublishBot ----------------------------------

    def publish_message(self, msg):
        self.print_msg('[publish]: {}'.format(msg))

    def push_message_to(self, msg, to_whom):
        self.print_msg('[push-to "{}"]: {}'.format(str(to_whom), msg))

    # Override for CommandBot ----------------------------------

    def _callback_on_command_not_supported(self, command, msg, from_who, reply, *a, **ka):
        self.print_msg('I do not support this command...')

    def _callback_on_non_command_msg(self, msg, from_who, reply, *a, **ka):
        pass

    def _command_extractor(self, msg):
        return hashtag_cmd_parse(msg)

    # -----------------------------------------------------------

    def onemsg(self, txt):
        self._callme_to_process_command_message(txt, 'cli-console', self.print_msg)

    def print_msg(self, msg):
        print('{}{}'.format(self.printout_prefix, msg))

    def mainloop(self):
        while True:
            try:
                txt = input(self.prompt)
                self.onemsg(txt)
            except KeyboardInterrupt:
                break
        self.print_msg('QUIT.')


if __name__ == '__main__':
    # Example Usage
    logger = logging.getLogger(__name__)
    c = CLIBot()
    while True:
        try:
            c.mainloop()
        except KeyboardInterrupt:
            logger.info('Canceled by user.')
            break
        except:
            logger.fatal('some problem have occurred, has to break down:', exc_info=True)
            break
    logger.info('stopped.')
