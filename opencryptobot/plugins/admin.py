import os
import sys
import time
import opencryptobot.emoji as emo

from opencryptobot.plugin import OpenCryptoPlugin
from opencryptobot.config import ConfigManager as Cfg


class Admin(OpenCryptoPlugin):

    def get_cmd(self):
        return "admin"

    @OpenCryptoPlugin.only_owner
    @OpenCryptoPlugin.send_typing
    def get_action(self, bot, update, args):
        # TODO: Set parameters in config
        # TODO: Get latest bot stats
        pass

    def get_usage(self):
        return None

    def get_description(self):
        return None

    def get_category(self):
        return None
