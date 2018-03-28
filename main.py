print('see ".ExampleBusiness"')

import logging

from BotImp.Wechat.WxGroupBot import WechatBot
from ExampleBusiness.ExampleCommands import load_commands

from config import TestConfig

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

# Load config
config = TestConfig()

# Initial wechat bot
wxbot = WechatBot(config.wx_id_group, config.wx_id_op, config.url_wechat_proxy)

# Load commands
load_commands(wxbot)

wxbot.startup_welcome("starting up.")

# Join thread
try:
    wxbot.join_thread()
except KeyboardInterrupt:
    logger.info("User request stop")

# Clean up
wxbot.stop()
print("stopped")

