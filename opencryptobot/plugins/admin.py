import logging
import opencryptobot.emoji as emo
import opencryptobot.utils as utl

from opencryptobot.plugin import OpenCryptoPlugin
from opencryptobot.config import ConfigManager as Cfg


class Admin(OpenCryptoPlugin):

    def get_cmd(self):
        return "admin"

    @OpenCryptoPlugin.only_owner
    @OpenCryptoPlugin.send_typing
    def get_action(self, bot, update, args):
        if not args:
            return

        sub_cmd = args[0]

        if "config" == sub_cmd.lower():
            keywords = utl.get_keywords(args)

            for key, value in keywords.items():
                self._change_cfg(key, value)

    def get_usage(self):
        return None

    def get_description(self):
        return None

    def get_category(self):
        return None

    def _change_cfg(self, key, value):
        pass
