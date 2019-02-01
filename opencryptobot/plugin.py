import inspect
import logging
import opencryptobot.emoji as emo

from telegram import ChatAction
from opencryptobot.config import ConfigManager as Cfg


class OpenCryptoPlugin:

    def __init__(self, telegram_bot):
        self.tgb = telegram_bot

    @classmethod
    def send_typing(cls, func):
        def _send_typing_action(self, bot, update, **kwargs):
            if update.message:
                user_id = update.message.chat_id
            elif update.callback_query:
                user_id = update.callback_query.message.chat_id
            else:
                return func(self, bot, update, **kwargs)

            bot.send_chat_action(
                chat_id=user_id,
                action=ChatAction.TYPING)

            return func(self, bot, update, **kwargs)
        return _send_typing_action

    @classmethod
    def only_owner(cls, func):
        def _only_owner(self, bot, update, **kwargs):
            if update.effective_user.id in Cfg.get("admin_id"):
                return func(self, bot, update, **kwargs)

        return _only_owner

    @classmethod
    def save_data(cls, func):
        def _save_data(self, bot, update, **kwargs):
            if Cfg.get("use_db"):
                if update.message:
                    usr = update.message.from_user
                    cmd = update.message.text
                    cht = update.message.chat
                    self.tgb.db.save(usr, cht, cmd)
                elif update.inline_query:
                    usr = update.effective_user
                    cmd = update.inline_query.query[:-1]
                    cht = update.effective_chat
                    self.tgb.db.save(usr, cht, cmd)

            return func(self, bot, update, **kwargs)
        return _save_data

    def handle_api_error(self, exception, update):
        cls_name = f"Class: {type(self).__name__}"
        logging.error(f"{repr(exception)} - {cls_name} - {update}")

        if update and update.message:
            msg = f"{emo.ERROR} {exception}"
            update.message.reply_text(msg)

    def get_cmd(self):
        method = inspect.currentframe().f_code.co_name
        raise NotImplementedError(f"Interface method '{method}' not implemented")

    def get_cmd_alt(self):
        return list()

    def get_action(self, bot, update, args):
        method = inspect.currentframe().f_code.co_name
        raise NotImplementedError(f"Interface method '{method}' not implemented")

    def get_usage(self):
        return None

    def get_description(self):
        return None

    def get_category(self):
        return None

    def inline_mode(self):
        return False


class Category:

    CHARTS = "Charts"
    PRICE = "Price"
    GENERAL = "General"
    NEWS = "News & Events"
    UTIL = "Utilities"
    FUN = "Fun"
    BOT = "Bot"

    @classmethod
    def get_categories(cls):
        categories = list()

        for k, v in vars(cls).items():
            if k.isupper() and isinstance(v, str):
                categories.append({k: v})

        return categories
