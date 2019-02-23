import opencryptobot.utils as utl

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
        if args:
            if args[0].lower() == "sql":
                args.pop(0)
                sql = " ".join(args)

                update.message.reply_text(repr(self.tgb.db.execute(sql)))
        else:
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
            InlineKeyboardButton("Number of Commands", callback_data="admin_stats_cmds"),
            InlineKeyboardButton("Number of Users", callback_data="admin_stats_usrs"),
            InlineKeyboardButton("Command Toplist", callback_data="admin_stats_cmdtop"),
            InlineKeyboardButton("Language Toplist", callback_data="admin_stats_langtop"),
            InlineKeyboardButton("<< BACK", callback_data="admin_back")]

        menu = self.build_menu(buttons)
        return InlineKeyboardMarkup(menu, resize_keyboard=True)

    def _callback(self, bot, update):
        query = update.callback_query

        # Statistics
        if query.data == "admin_stats":
            bot.edit_message_text(
                text=f"Choose from available statistics",
                chat_id=query.message.chat_id,
                message_id=query.message.message_id,
                reply_markup=self._keyboard_stats())

        # Statistics - << BACK
        elif query.data == "admin_back":
            usr = update.effective_user.first_name

            bot.edit_message_text(
                text=f"Welcome {usr}.\nChoose an option",
                chat_id=query.message.chat_id,
                message_id=query.message.message_id,
                reply_markup=self._keyboard_options())

        # Statistics - Number of Commands
        elif query.data == "admin_stats_cmds":
            sql = "SELECT COUNT(command) FROM cmd_data"
            data = self.tgb.db.execute(sql)
            bot.send_message(
                chat_id=update.effective_user.id,
                text=f"`Commands: {data[0][0]}`",
                parse_mode=ParseMode.MARKDOWN)

        # Statistics - Number of Users
        elif query.data == "admin_stats_usrs":
            sql = "SELECT COUNT(user_id) FROM users"
            data = self.tgb.db.execute(sql)
            bot.send_message(
                chat_id=update.effective_user.id,
                text=f"`Users: {data[0][0]}`",
                parse_mode=ParseMode.MARKDOWN)

        # Statistics - Command Toplist
        elif query.data == "admin_stats_cmdtop":
            sql = "SELECT command, COUNT(command) AS number " \
                  "FROM cmd_data " \
                  "GROUP BY command " \
                  "ORDER BY 2 DESC " \
                  "LIMIT 10"
            data = self.tgb.db.execute(sql)

            msg = str()
            for row in data:
                msg += utl.esc_md(f"{row[1]} {row[0]}\n")

            bot.send_message(
                chat_id=update.effective_user.id,
                text=f"`Command Toplist:\n\n{msg}`",
                parse_mode=ParseMode.MARKDOWN)

        # Statistics - Language Toplist
        elif query.data == "admin_stats_langtop":
            sql = "SELECT language, COUNT(language) AS lang " \
                  "FROM users " \
                  "GROUP BY language " \
                  "ORDER BY 2 DESC " \
                  "LIMIT 10"
            data = self.tgb.db.execute(sql)

            msg = str()
            for row in data:
                msg += f"{row[1]} {row[0]}\n"

            bot.send_message(
                chat_id=update.effective_user.id,
                text=f"`Language Toplist:\n\n{msg}`",
                parse_mode=ParseMode.MARKDOWN)
