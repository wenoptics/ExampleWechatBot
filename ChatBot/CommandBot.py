import logging


class CommandBot:
    """
    CommandBot is about retrieving message (which probably contain some command) from end-user,
        and perform some actions based on the command
    """

    def __init__(self):
        super().__init__()

        # Commands will be auto added into these list by @register_command
        self.list_supported_command = []
        self.list_supported_command_private = []

        # A <command_str>: <handler function> dictionary
        self.dict_command_handler = {}

        self.logger = logging.getLogger('CommandBot')
        self.logger.setLevel(logging.DEBUG)

    # todo Support accept command as list
    def register_command(self, command_str: str, is_private=False):
        """
        Decorator for registering command call handlers

        Usage example:

        @register_command('myCommand0')
        def on_my_command_0(cmdbot, message_text, from_who, reply):
            print(cmdbot, message_text, from_who, reply)
            reply('I received "%s"' % msg)
            ...

        :param is_private:
        :param command_str:
        :return:
        """

        def register_handler(dst_func):

            # Check is command_str valid.
            if type(command_str) is not str or command_str == '':
                self.logger.error('command_str "{}" not valid'.format(command_str))
                raise ValueError('command_str "{}" not valid'.format(command_str))

            # Save this handler somewhere so that later we can find it
            self.dict_command_handler[command_str] = dst_func

            save_list = self.list_supported_command
            if is_private: save_list = self.list_supported_command_private
            # Save into a list as well
            if command_str not in save_list:
                save_list.append(command_str)

            self.logger.info('function "{}" registered for command "{}"'
                             .format(dst_func.__name__, command_str))
            return dst_func

        return register_handler

    def _command_extractor(self, msg) -> (str, str):
        """
        Extract the command string from the given message
        Return the command string and text left

        You have to implement this function so that command string can be extracted
            from an arbitrary string message
            Return None if no command string found in the message
        :param msg:
        :return:
        """
        raise NotImplementedError

    def _callback_on_command_not_supported(self, command, msg, from_who, reply, *a, **ka):
        """
        This is called when a command is recognized but not in the support_list
            Do something if you like.
        :param command:
        :param msg:
        :param from_who:
        :param reply: handler for replying some messages
        :return:
        """
        raise NotImplementedError

    def _callback_on_non_command_msg(self, msg, from_who, reply, *a, **ka):
        """
        This is called when there's no command in a message (a normal text message)
        :param msg:
        :param from_who:
        :param reply: handler for replying some messages
        :return:
        """
        raise NotImplementedError

    def _callme_to_process_command_message(self, msg, from_who, reply, *a, **ka):
        """
        This should be called when receiving a message
        :param msg:
        :param from_who:
        :param reply: handler for replying some messages
        :return:
        """
        self.__on_message(msg, from_who, reply, *a, **ka)

    def __on_message(self, msg, from_who, reply, *a, **ka):
        """Handles incoming message"""
        SUPRESS_RAISE = False
        command_str, message_text = self.__try_to_parse_message(msg)
        if command_str is None:
            # Then this is a normal text message
            try:
                self._callback_on_non_command_msg(msg, from_who, reply, *a, **ka)
            except:
                if not SUPRESS_RAISE: raise
                self.logger.error('error occur in _callback_on_non_command_msg()', exc_info=True)
        elif command_str not in self.list_supported_command \
                and command_str not in self.list_supported_command_private:
            # Command recognized but not supported (not implementation offered)
            try:
                self._callback_on_command_not_supported(command_str, msg, from_who, reply)
            except:
                if not SUPRESS_RAISE: raise
                self.logger.error('error occur in _callback_on_command_not_supported()', exc_info=True)
        else:
            # Call the relevant command handler
            command_handler = self.dict_command_handler.get(command_str)
            try:
                self.logger.debug(
                    'command "{}" exec --> "{}({},{})"'.format(command_str, command_handler, str(a), str(ka)))
                command_handler.__call__(self, message_text, from_who, reply, *a, **ka)
            except:
                self.logger.error('Error occurred in executing command handler "{}"'.format(command_handler.__name__))
                if not SUPRESS_RAISE:
                    raise

    def __try_to_parse_message(self, msg) -> (str, str):
        try:
            command, left_txt = self._command_extractor(msg)
            return command, left_txt
        except:
            self.logger.error('error occur when parsing message', exc_info=True)
        return None, None


if __name__ == '__main__':
    exit(0)

    # Usage Examples:

    def receive_one_coming_message(): pass
    def your_reply_handler(): pass

    class MyBot(CommandBot):
        def _callback_on_command_not_supported(self, command, msg, from_who, reply, *a, **ka):
            print('Warning: command "{}" not supported.'.format(command))

        def _callback_on_non_command_msg(self, msg, from_who, reply, *a, **ka):
            print('talker "{}" says "{}", this is a regular message'.format(from_who, msg))

        def _command_extractor(self, msg):
            # Define a command starts with "#"
            try:
                import re
                match = re.search('#(\S+)\s*(.*)', msg)
                if match:
                    return match.group(1), match.group(2)
            except:
                pass
            return None, None

        def __init__(self):

            super().__init__()

            # Do your stuff...
            new_message = receive_one_coming_message()
            self._callme_to_process_command_message(new_message.text, "Someone", your_reply_handler,
                                                    SomeOfYourExtraParams="SomeValue")


    mybot = CommandBot()


    @mybot.register_command("Hello", is_private=True)
    def on_request_something(bot: CommandBot, msg, chat, reply,
                             SomeOfYourExtraParams="SomeDefaultValue", *args, **kwargs):

        print('in on_request_something() {} {} {}'
              .format(msg, chat, SomeOfYourExtraParams))

        # Extract your stuff from request input
        import re
        something = re.search(r'\w+', msg)
        if something:
            something = something.group(0)
        else:
            something = ''

        ret_msgs = "My return message"
        reply(ret_msgs)
