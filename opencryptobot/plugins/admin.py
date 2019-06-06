import opencryptobot.utils as utl
import opencryptobot.emoji as emo

from collections import OrderedDict
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
                if Cfg.get("database", "use_db"):
                    args.pop(0)

                    sql = " ".join(args)
                    data = self.tgb.db.execute_sql(sql)

                    if data["error"]:
                        msg = data["error"]
                    elif data["result"]:
                        msg = '\n'.join(str(s) for s in data["result"])
                    else:
                        msg = f"{emo.INFO} No data returned"

                    update.message.reply_text(msg)
                else:
                    update.message.reply_text(f"{emo.INFO} Database not enabled")

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
                if Cfg.get("database", "use_db"):
                    args.pop(0)

                    sql = self.get_sql("global_msg")
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
                else:
                    update.message.reply_text(f"{emo.INFO} Database not enabled")

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
            InlineKeyboardButton("Language Toplist", callback_data="admin_langtop"),
            InlineKeyboardButton("User Toplist", callback_data="admin_usertop"),
            InlineKeyboardButton("Daily Users", callback_data="admin_userdaily")]

        menu = self.build_menu(buttons)
        return InlineKeyboardMarkup(menu, resize_keyboard=True)

    def _callback(self, bot, update):
        query = update.callback_query

        if not Cfg.get("database", "use_db"):
            bot.answer_callback_query(query.id, text="Database not enabled")
            return

        # Statistics - Number of Commands
        if query.data == "admin_cmds":
            data = self.tgb.db.execute_sql(self.get_sql("number_cmd"))

            if data["error"]:
                msg = data["error"]
            elif data["result"]:
                msg = f"`Commands: {data['result'][0][0]}`"
            else:
                msg = f"{emo.INFO} No data returned"

            bot.send_message(
                text=msg,
                chat_id=update.effective_user.id,
                parse_mode=ParseMode.MARKDOWN)

        # Statistics - Number of Users
        elif query.data == "admin_usrs":
            data = self.tgb.db.execute_sql(self.get_sql("number_usr"))

            if data["error"]:
                msg = data["error"]
            elif data["result"]:
                msg = f"`Users: {data['result'][0][0]}`"
            else:
                msg = f"{emo.INFO} No data returned"

            bot.send_message(
                text=msg,
                chat_id=update.effective_user.id,
                parse_mode=ParseMode.MARKDOWN)

        # Statistics - Command Toplist
        elif query.data == "admin_cmdtop":
            data = self.tgb.db.execute_sql(self.get_sql("cmd_top"))

            msg = str()
            if data["error"]:
                msg = data["error"]
            elif data["result"]:
                for row in data["result"] or []:
                    msg += utl.esc_md(f"{row[1]} {row[0]}\n")
            else:
                msg = f"{emo.INFO} No data returned"

            bot.send_message(
                text=f"`Command Toplist:\n\n{msg}`",
                chat_id=update.effective_user.id,
                parse_mode=ParseMode.MARKDOWN)

        # Statistics - Language Toplist
        elif query.data == "admin_langtop":
            data = self.tgb.db.execute_sql(self.get_sql("lang_top"))

            msg = str()
            if data["error"]:
                msg = data["error"]
            elif data["result"]:
                for row in data["result"] or []:
                    msg += f"{row[1]} {row[0]}\n"
            else:
                msg = f"{emo.INFO} No data returned"

            bot.send_message(
                text=f"`Language Toplist:\n\n{msg}`",
                chat_id=update.effective_user.id,
                parse_mode=ParseMode.MARKDOWN)

        # Statistics - User Toplist
        elif query.data == "admin_usertop":
            data = self.tgb.db.execute_sql(self.get_sql("user_top"))

            msg = str()
            if data["error"]:
                msg = data["error"]
            elif data["result"]:
                for row in data["result"] or []:
                    msg += f"{row[1]} {row[0]}\n"
            else:
                msg = f"{emo.INFO} No data returned"

            bot.send_message(
                text=f"`User Toplist:\n\n{msg}`",
                chat_id=update.effective_user.id,
                parse_mode=ParseMode.MARKDOWN)

        # Statistics - Daily Users
        elif query.data == "admin_userdaily":
            data = self.tgb.db.execute_sql(self.get_sql("user_daily"))

            if data["error"]:
                msg = data["error"]
            elif data["result"]:
                o_dict = OrderedDict()
                for row in data["result"] or []:
                    date = row[0].split(" ")[0]
                    if date not in o_dict:
                        o_dict[date] = list()
                    o_dict[date].append(row[1])

                msg = str()
                for k, v in o_dict.items():
                    msg += f"\n{k}\n"
                    for name in v:
                        msg += f"{name}\n"
            else:
                msg = f"{emo.INFO} No data returned"

            bot.send_message(
                text=f"`Daily Users:\n{msg}`",
                chat_id=update.effective_user.id,
                parse_mode=ParseMode.MARKDOWN)

        bot.answer_callback_query(query.id, text="Query executed")
