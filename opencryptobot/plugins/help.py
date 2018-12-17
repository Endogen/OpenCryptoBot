from telegram import ParseMode
from opencryptobot.telegrambot import TelegramBot
from opencryptobot.plugin import OpenCryptoPlugin, Category


class Help(OpenCryptoPlugin):

    def get_cmd(self):
        return "help"

    @OpenCryptoPlugin.send_typing
    def get_action(self, bot, update, args):
        help_msg = str("*Available commands*\n\n")

        # TODO: Create list of lists for the categories
        categories = Category.get_categories()

        # TODO: Add every plugin to corresponding list
        for plugin in TelegramBot.plugins:
            if plugin.get_category() and plugin.get_description():
                help_msg += f"/{plugin.get_cmd()} - {plugin.get_description()}\n"

        update.message.reply_text(text=help_msg, parse_mode=ParseMode.MARKDOWN)

    def get_usage(self):
        return None

    def get_description(self):
        return None

    def get_category(self):
        return None
