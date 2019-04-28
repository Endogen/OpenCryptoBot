import opencryptobot.utils as utl
import opencryptobot.emoji as emo

from opencryptobot.plugin import OpenCryptoPlugin
from opencryptobot.config import ConfigManager as Cfg
from telegram import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackQueryHandler


class Admin(OpenCryptoPlugin):

    def __init__(self, telegram_bot):
        super().__init__(telegram_bot)
        self.tgb.dispatcher.add_handler(
            CallbackQueryHandler(
                self._callback,
                pattern="^admin"))

    def get_cmds(self):
        return ["admin"]

    @OpenCryptoPlugin.only_owner
    @OpenCryptoPlugin.send_typing
    def get_action(self, bot, update, args):
        if args:
            command = args[0].lower()

            # Execute raw SQL
            if command == "sql":
                args.pop(0)
                sql = " ".join(args)

                update.message.reply_text(repr(self.tgb.db.execute_sql(sql)))

            # Change configuration
            elif command == "cfg":
                args.pop(0)
                v = args[-1]
                v = v.lower()
                args.pop(-1)

                # Convert to boolean
                if v == "true" or v == "false":
                    v = utl.str2bool(v)

                # Convert to integer
                elif v.isnumeric():
                    v = int(v)

                # Convert to null
                elif v == "null" or v == "none":
                    v = None

                try:
                    Cfg.set(v, *args)
                except Exception as e:
                    return self.handle_error(e, update)

                update.message.reply_text("Config changed")

            # Send global message
            elif command == "msg":
                args.pop(0)

                sql = "SELECT user_id FROM users"
                data = self.tgb.db.execute_sql(sql)

                title = "This is a global message to " \
                        "every user of @OpenCryptoBot:\n\n"

                msg = " ".join(args)

                for user_id in data or []:
                    try:
                        bot.send_message(
                            chat_id=user_id[0],
                            text=f"{title}{msg}")
                    except Exception as e:
                        self.handle_error(e, update, send_error=False)

            # Manage plugins
            elif command == "plg":
                args.pop(0)

                # LOAD plugin
                if args[0].lower() == "load":
                    self.tgb.reload_plugin(args[1])
                    update.message.reply_text("Plugin loaded")

                # UNLOAD plugin
                elif args[0].lower() == "unload":
                    self.tgb.remove_plugin(args[1])
                    update.message.reply_text("Plugin unloaded")

        else:
            usr = update.effective_user.first_name

            update.message.reply_text(
                text=f"Welcome {usr}.\nChoose a statistic",
                reply_markup=self._keyboard_stats())

    def get_usage(self):
        return None

    def get_description(self):
        return None

    def get_category(self):
        return None

    def _keyboard_stats(self):
        buttons = [
            InlineKeyboardButton("Number of Commands", callback_data="admin_cmds"),
            InlineKeyboardButton("Number of Users", callback_data="admin_usrs"),
            InlineKeyboardButton("Command Toplist", callback_data="admin_cmdtop"),
            InlineKeyboardButton("Language Toplist", callback_data="admin_langtop")]

        menu = self.build_menu(buttons)
        return InlineKeyboardMarkup(menu, resize_keyboard=True)

    def _callback(self, bot, update):
        query = update.callback_query

        # Statistics - Number of Commands
        if query.data == "admin_cmds":
            sql = "SELECT COUNT(command) FROM cmd_data"
            data = self.tgb.db.execute_sql(sql)

            if not data:
                bot.send_message(
                    chat_id=update.effective_user.id,
                    text=f"`{emo.INFO} No results`",
                    parse_mode=ParseMode.MARKDOWN)
                return

            bot.send_message(
                chat_id=update.effective_user.id,
                text=f"`Commands: {data[0][0]}`",
                parse_mode=ParseMode.MARKDOWN)

        # Statistics - Number of Users
        elif query.data == "admin_usrs":
            sql = "SELECT COUNT(user_id) FROM users"
            data = self.tgb.db.execute_sql(sql)

            if not data:
                bot.send_message(
                    chat_id=update.effective_user.id,
                    text=f"`{emo.INFO} No results`",
                    parse_mode=ParseMode.MARKDOWN)
                return

            bot.send_message(
                chat_id=update.effective_user.id,
                text=f"`Users: {data[0][0]}`",
                parse_mode=ParseMode.MARKDOWN)

        # Statistics - Command Toplist
        elif query.data == "admin_cmdtop":
            sql = "SELECT command, COUNT(command) AS number " \
                  "FROM cmd_data " \
                  "GROUP BY command " \
                  "ORDER BY 2 DESC " \
                  "LIMIT 25"
            data = self.tgb.db.execute_sql(sql)

            msg = str()
            for row in data or []:
                msg += utl.esc_md(f"{row[1]} {row[0]}\n")

            if not msg:
                bot.send_message(
                    chat_id=update.effective_user.id,
                    text=f"`{emo.INFO} No results`",
                    parse_mode=ParseMode.MARKDOWN)
                return

            bot.send_message(
                chat_id=update.effective_user.id,
                text=f"`Command Toplist:\n\n{msg}`",
                parse_mode=ParseMode.MARKDOWN)

        # Statistics - Language Toplist
        elif query.data == "admin_langtop":
            sql = "SELECT language, COUNT(language) AS lang " \
                  "FROM users " \
                  "GROUP BY language " \
                  "ORDER BY 2 DESC " \
                  "LIMIT 15"
            data = self.tgb.db.execute_sql(sql)

            msg = str()
            for row in data or []:
                msg += f"{row[1]} {row[0]}\n"

            if not msg:
                bot.send_message(
                    chat_id=update.effective_user.id,
                    text=f"`{emo.INFO} No results`",
                    parse_mode=ParseMode.MARKDOWN)
                return

            bot.send_message(
                chat_id=update.effective_user.id,
                text=f"`Language Toplist:\n\n{msg}`",
                parse_mode=ParseMode.MARKDOWN)
