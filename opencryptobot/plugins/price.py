import opencryptobot.emoji as emo

from telegram import ParseMode
from opencryptobot.plugin import OpenCryptoPlugin


# TODO: Implement
class Price(OpenCryptoPlugin):

    def get_cmd(self):
        return "p"

    @OpenCryptoPlugin.send_typing
    @OpenCryptoPlugin.save_data
    def get_action(self, bot, update, args):
        update.message.reply_text(
            text=f"{emo.STARS} *NOT IMPLEMENTED YET* {emo.STARS}",
            parse_mode=ParseMode.MARKDOWN)

    def get_usage(self):
        return "`/p [COIN] | [PAIR]`"

    def get_description(self):
        return "Show the price of a coin"
