from redis import Redis


class RedisConnect(object):
    _INSTANCE = None
    FLAG = False

    def __init__(self, host, port, db=0, **kwargs):
        if not self.__class__.FLAG:
            self.redis = Redis(host=host, port=port, db=db, **kwargs)
            self.__class__.FLAG = True

    def __getattr__(self, item):
        assert hasattr(self.redis, item)
        return getattr(self.redis, item)

    def __new__(cls, *args, **kwargs):
        if cls._INSTANCE is None:
            cls._INSTANCE = object.__new__(cls)
        return cls._INSTANCE
