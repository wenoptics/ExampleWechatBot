import datetime
import inspect
import logging

from pyWechatProxyClient.api.model.Chat import Chat
logger = logging.getLogger(__name__)


class SessionExpiredError(RuntimeError):
    pass


class Session(dict):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Expired datetime
        self._dt_expiration = None  # None means never expired.

    @property
    def is_expired(self):
        return self._dt_expiration is not None\
               and datetime.datetime.now() > self._dt_expiration

    @property
    def expiration(self) -> datetime.datetime:
        """Session过期的datetime"""
        return self._dt_expiration

    def __getitem__(self, key):
        if self.is_expired:
            raise SessionExpiredError('session expired')
        return self.__dict__[key]

    def __setitem__(self, key, value):
        if self.is_expired:
            raise SessionExpiredError('session expired')
        self.__dict__[key] = value

    def __len__(self):
        return len(self.__dict__)

    def __repr__(self):
        return repr(self.__dict__)

    def get(self, k, d=None):
        if self.is_expired:
            raise SessionExpiredError('session expired')
        if k not in self.__dict__.keys():
            return d
        return self.__dict__[k]

    def set_expired(self):
        """
        Expired immediately
        :return:
        """
        self._dt_expiration = datetime.datetime.now() - datetime.timedelta(weeks=1)

    def renew(self, expire_dt: datetime.datetime):
        self._dt_expiration = expire_dt
        logger.debug('Session expiration set to {}'.format(self._dt_expiration))


class CommandSession(Session):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._handlers = {}

    def add_command(self, cmd: str, handler):
        if self.is_expired:
            raise SessionExpiredError('session expired')
        if not inspect.isfunction(handler):
            raise ValueError('handler is not a function.')

        self._handlers[cmd] = handler

    def invoke_command(self, cmd: str, *args, **kwargs):
        if self.is_expired:
            raise SessionExpiredError('session expired')

        handler = self._handlers.get(cmd)
        if handler is None:
            raise KeyError('no such command.')
        handler.__call__(self, *args, **kwargs)


class ConversationSessionManager:
    __session_table = {}

    @classmethod
    def new_session_by_unique(cls, unique: str, expire_after: datetime.timedelta=None):
        session = Session()
        if expire_after is not None:
            session.renew(datetime.datetime.now() + expire_after)
        cls.__session_table[unique] = session
        return session

    @classmethod
    def get_session_by_unique(cls, unique: str):
        session = cls.__session_table.get(unique)
        if session is not None and session.is_expired:
            # Delete the expired session.
            del cls.__session_table[unique]
            return None
        return session

    @classmethod
    def new_session(cls, chat: Chat, expire_after: datetime.timedelta=None):
        unique = chat.talker_id
        return cls.new_session_by_unique(unique, expire_after)

    @classmethod
    def new_command_session(cls, chat: Chat, expire_after: datetime.timedelta=None):
        unique = chat.talker_id
        cs = CommandSession()
        if expire_after is not None:
            cs.renew(datetime.datetime.now() + expire_after)
        cls.__session_table[unique] = cs
        return cs

    @classmethod
    def get_session(cls, chat: Chat):
        unique = chat.talker_id
        return cls.get_session_by_unique(unique)

    @classmethod
    def del_session(cls, chat: Chat):
        unique = chat.talker_id
        if unique not in cls.__session_table.keys():
            raise ValueError('session not existed')

        del cls.__session_table[unique]

    @classmethod
    def del_expired(cls):
        for k, session in cls.__session_table:
            if session.is_expired:
                del cls.__session_table[k]