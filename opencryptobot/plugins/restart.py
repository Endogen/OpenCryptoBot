import os
import sys
import time
import opencryptobot.emoji as emo

from telegram.ext import CommandHandler
from opencryptobot.plugin import OpenCryptoPlugin


class Restart(OpenCryptoPlugin):

    def get_handler(self):
        return CommandHandler("restart", self._restart)

    @OpenCryptoPlugin.add_user
    @OpenCryptoPlugin.only_owner
    @OpenCryptoPlugin.send_typing
    def _restart(self, bot, update):
        msg = f"{emo.WAIT} Bot is restarting..."
        update.message.reply_text(msg)

        time.sleep(0.2)
        os.execl(sys.executable, sys.executable, *sys.argv)
