import opencryptobot.emoji as emo

from telegram import ParseMode
from telegram.ext import CommandHandler
from opencryptobot.plugin import OpenCryptoPlugin


# TODO: Implement
class Price(OpenCryptoPlugin):

    def get_handler(self):
        return CommandHandler("p", self._shutdown)

    @OpenCryptoPlugin.add_user
    def _shutdown(self, bot, update):
        update.message.reply_text(
            text=f"{emo.STARS} *NOT IMPLEMENTED YET* {emo.STARS}",
            parse_mode=ParseMode.MARKDOWN)
