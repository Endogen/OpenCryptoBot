import opencryptobot.emoji as emo

from telegram import ParseMode
from opencryptobot.plugin import OpenCryptoPlugin


class Start(OpenCryptoPlugin):

    def get_cmd(self):
        return "start"

    def get_action(self, bot, update, args):
        update.message.reply_text(
            text=f"{emo.STARS} *Welcome to OpenCryptoBot!* {emo.STARS}",
            parse_mode=ParseMode.MARKDOWN)

    def get_usage(self):
        return None

    def get_description(self):
        return None
