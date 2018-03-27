class Config:
    wx_id_group = ''
    wx_id_op = ''
    version = '0.1.0'
    url_wechat_proxy = 'ws://'


class ProductionConfig(Config):
    pass


class TestConfig(Config):
    pass
