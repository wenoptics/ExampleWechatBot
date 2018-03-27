import config
from BotImp.Wechat.WxGroupBot import WechatBot
from ChatBot.CommandBot import CommandBot

if __name__ == '__main__':
    # Example:

    config = config.TestConfig()
    wxbot = WechatBot(config.wx_id_group, config.wx_id_op, config.url_wechat_proxy)

    @wxbot.register_command("Hello", is_private=True)
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

        ret_msgs = "Hi {}, welcome".format(something)
        reply(ret_msgs)

    # And send "#Hello wen", it replies "Hi wen, welcome"
