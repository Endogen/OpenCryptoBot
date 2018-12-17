from telegram import ParseMode
from opencryptobot.plugin import OpenCryptoPlugin
from opencryptobot.telegrambot import TelegramBot


class Help(OpenCryptoPlugin):

    def get_cmd(self):
        return "help"

    @OpenCryptoPlugin.send_typing
    def get_action(self, bot, update, args):
        help_msg = str("*Available commands*\n\n")
        for plugin in TelegramBot.plugins:
            if plugin.get_description():
                help_msg += f"/{plugin.get_cmd()} - {plugin.get_description()}\n"

        update.message.reply_text(text=help_msg, parse_mode=ParseMode.MARKDOWN)

    def get_usage(self):
        return None

    def get_description(self):
        return None
