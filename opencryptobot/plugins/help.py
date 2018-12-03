from telegram import ParseMode
from opencryptobot.plugin import OpenCryptoPlugin


class Help(OpenCryptoPlugin):

    def get_cmd(self):
        return "help"

    @OpenCryptoPlugin.send_typing
    def get_action(self, bot, update, args):
        update.message.reply_text(
            text="Some help here",
            parse_mode=ParseMode.MARKDOWN)

    def get_usage(self):
        return None

    def get_description(self):
        return None
