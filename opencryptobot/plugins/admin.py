from opencryptobot.plugin import OpenCryptoPlugin
from telegram import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackQueryHandler


class Admin(OpenCryptoPlugin):

    def __init__(self, telegram_bot):
        super().__init__(telegram_bot)
        self.tgb.dispatcher.add_handler(
            CallbackQueryHandler(
                self._callback,
                pattern="^admin"))

    def get_cmd(self):
        return "admin"

    @OpenCryptoPlugin.only_owner
    @OpenCryptoPlugin.send_typing
    def get_action(self, bot, update, args):
        usr = update.effective_user.first_name

        update.message.reply_text(
            text=f"Welcome {usr}.\nChoose an option",
            reply_markup=self._keyboard_options())

    def get_usage(self):
        return None

    def get_description(self):
        return None

    def get_category(self):
        return None

    def _change_cfg(self, key, value):
        pass

    def _keyboard_options(self):
        buttons = [
            InlineKeyboardButton("Statistics", callback_data="admin_stats"),
            InlineKeyboardButton("Global Message", callback_data="admin_msg"),
            InlineKeyboardButton("Manage Plugins", callback_data="admin_plugins")]

        menu = self.build_menu(buttons)
        return InlineKeyboardMarkup(menu, resize_keyboard=True)

    def _keyboard_stats(self):
        buttons = [
            InlineKeyboardButton("Commands count", callback_data="admin_stats_cmds"),
            InlineKeyboardButton("User count", callback_data="admin_stats_usrs"),
            InlineKeyboardButton("Commands Today", callback_data="admin_stats_cmdstd"),
            InlineKeyboardButton("New Users Today", callback_data="admin_stats_newusrs"),
            InlineKeyboardButton("<< BACK", callback_data="admin_back")]

        menu = self.build_menu(buttons)
        return InlineKeyboardMarkup(menu, resize_keyboard=True)

    def _callback(self, bot, update):
        usr = update.effective_user.first_name
        query = update.callback_query

        if query.data == "admin_stats":
            bot.edit_message_text(
                text=f"Choose from available statistics",
                chat_id=query.message.chat_id,
                message_id=query.message.message_id,
                reply_markup=self._keyboard_stats())

        elif query.data == "admin_back":
            bot.edit_message_text(
                text=f"Welcome {usr}. Choose an option",
                chat_id=query.message.chat_id,
                message_id=query.message.message_id,
                reply_markup=self._keyboard_options())

        elif query.data == "admin_stats_cmds":
            sql = "SELECT COUNT(command) FROM cmd_data"
            data = self.tgb.db.execute(sql)
            bot.send_message(
                chat_id=update.effective_user.id,
                text=f"Commands: {data[0][0]}")

        elif query.data == "admin_stats_usrs":
            sql = "SELECT COUNT(user_id) FROM users"
            data = self.tgb.db.execute(sql)
            bot.send_message(
                chat_id=update.effective_user.id,
                text=f"Users: {data[0][0]}")
