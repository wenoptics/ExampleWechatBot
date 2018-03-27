
class PublishBot:
    """PublishBot can only publish messages(won't handle receiving messages)"""
    def __init__(self):
        self.__has_op = False
        self.__op = None

    def publish_message(self, msg):
        raise NotImplementedError

    def push_message_to(self, msg, to_whom):
        raise NotImplementedError

    def push_message_to_op(self, msg):
        if not self.__has_op:
            raise ValueError("This bot has no op")
        self.push_message_to(msg, self.__op)

    def set_op(self, who):
        self.__op = who
        self.__has_op = True
