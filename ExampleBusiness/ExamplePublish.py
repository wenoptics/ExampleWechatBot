from BotImp.Wechat.WxGroupBot import WechatBot
import config

if __name__ == '__main__':
    # Example:

    config = config.TestConfig()
    wxbot = WechatBot(config.wx_id_group, config.wx_id_op, config.url_wechat_proxy)

    wxbot.publish_message("hi, this is {}".format("Wenop"))
