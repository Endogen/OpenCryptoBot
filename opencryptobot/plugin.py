import inspect

from telegram import ChatAction
from opencryptobot.config import ConfigManager as Cfg


class OpenCryptoPlugin:

    def __init__(self, updater, db):
        self.updater = updater
        self.db = db

    # Decorator to show user that bot is retrieving data
    @classmethod
    def send_typing(cls, func):
        def _send_typing_action(*args, **kwargs):
            self, bot, update = args

            if update.message:
                user_id = update.message.chat_id
            else:
                user_id = update.callback_query.message.chat_id

            bot.send_chat_action(
                chat_id=user_id,
                action=ChatAction.TYPING)

            return func(self, bot, update, **kwargs)
        return _send_typing_action

    # Decorator to add users if not already present
    @classmethod
    def add_user(cls, func):
        def _add_user(self, bot, update, **kwargs):
            usr = update.message.from_user

            if not self.db.user_exists(usr.id):
                self.db.add_user(usr)

            return func(self, bot, update, **kwargs)
        return _add_user

    @classmethod
    def only_owner(cls, func):
        def _only_owner(self, bot, update, **kwargs):

            if Cfg.get("admin_id") == update.effective_user.id:
                return func(self, bot, update, **kwargs)

        return _only_owner

    @classmethod
    def save_command(cls, func):
        def _save_command(self, bot, update, **kwargs):
            usr_id = update.message.from_user.id
            cmd = update.message.text

            if Cfg.get("use_db"):
                self.db.save_cmd(usr_id, cmd)

            return func(self, bot, update, **kwargs)
        return _save_command

    @staticmethod
    def trm_zro(value_to_trim, decimals=8):
        if isinstance(value_to_trim, float):
            return (("%." + str(decimals) + "f") % value_to_trim).rstrip("0").rstrip(".")

        elif isinstance(value_to_trim, str):
            str_list = value_to_trim.split(" ")

            for i in range(len(str_list)):
                old_s = str_list[i]

                if old_s.replace(".", "").replace(",", "").isdigit():
                    new_s = str((("%." + str(decimals) + "f") % float(old_s)).rstrip("0").rstrip("."))
                    str_list[i] = new_s

            return " ".join(str_list)

        else:
            return value_to_trim

    def get_handler(self):
        method = inspect.currentframe().f_code.co_name
        raise NotImplementedError(f"Interface method '{method}' not implemented")

    def get_usage(self):
        method = inspect.currentframe().f_code.co_name
        raise NotImplementedError(f"Interface method '{method}' not implemented")
