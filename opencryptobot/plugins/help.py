import opencryptobot.emoji as emo

from telegram import ParseMode
from telegram.ext import CommandHandler
from opencryptobot.plugin import OpenCryptoPlugin


# TODO: Has to be identical to 'start'
# TODO: Automatically for every plugin, derive usage, desc and cmd
class Start(OpenCryptoPlugin):

    def get_handler(self):
        return CommandHandler("start", self._start)

    @OpenCryptoPlugin.add_user
    def _start(self, bot, update):
        update.message.reply_text(
            text=f"{emo.STARS} *Welcome to OpenCryptoBot!* {emo.STARS}",
            parse_mode=ParseMode.MARKDOWN)
