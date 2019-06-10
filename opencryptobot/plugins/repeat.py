import logging
import opencryptobot.emoji as emo
import opencryptobot.utils as utl

from sqlite3 import IntegrityError
from opencryptobot.config import ConfigManager as Cfg
from opencryptobot.plugin import OpenCryptoPlugin, Category
from telegram import ParseMode, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler


class Repeat(OpenCryptoPlugin):

    def __init__(self, telegram_bot):
        super().__init__(telegram_bot)

        # Check if database is enabled since this plugin needs it
        if not Cfg.get("database", "use_db"):
            msg = f"Plugin '{type(self).__name__}' " \
                  f"can't be used since database is disabled"
            logging.warning(msg)

    def get_cmds(self):
        return ["re", "repeat", "timer"]

    @OpenCryptoPlugin.save_data
    @OpenCryptoPlugin.send_typing
    def get_action(self, bot, update, args):
        # Check if database is enabled
        if not Cfg.get("database", "use_db"):
            update.message.reply_text(
                text=f"{emo.ERROR} Plugin '{type(self).__name__}' "
                     f"can't be used since database is disabled",
                parse_mode=ParseMode.MARKDOWN)
            return

        # Check if any arguments provided
        if not args:
            update.message.reply_text(
                text=f"Usage:\n{self.get_usage()}",
                parse_mode=ParseMode.MARKDOWN)
            return

        # 'list' argument - show all repeaters for a user
        if args[0].lower() == "list":
            chat_id = update.message.chat.id
            user_id = update.message.from_user.id

            repeaters = self.tgb.db.read_rep(user_id, chat_id)

            if repeaters:
                for rep in repeaters:
                    chat = self.tgb.db.read_chat(rep[2])
                    chat_name = chat[2] if chat else None

                    update.message.reply_text(
                        text=f"Command:\n`{rep[3]}`\n"
                             f"Chat:\n`{chat_name}`\n\n"
                             f"↺ {rep[4]} seconds\n\n"
                             f"(ID: {rep[0]})",
                        parse_mode=ParseMode.MARKDOWN,
                        reply_markup=self._keyboard_remove_rep())
                return
            else:
                update.message.reply_text(f"{emo.INFO} No repeaters active")
                return

        # Extract time interval
        interval = str()
        if args[0].startswith("i="):
            interval = args[0].replace("i=", "")
            args.pop(0)

        # Check if time interval is provided
        if not interval:
            update.message.reply_text(
                text=f"{emo.ERROR} Time interval has to be provided",
                parse_mode=ParseMode.MARKDOWN)
            return

        # In seconds
        interval = utl.get_seconds(interval)

        # Check if interval was successfully converted to seconds
        if not interval:
            update.message.reply_text(
                text=f"{emo.ERROR} Wrong format for time interval",
                parse_mode=ParseMode.MARKDOWN)
            return

        # Check for command to repeat
        if not args:
            update.message.reply_text(
                text=f"{emo.ERROR} Provide command to repeat",
                parse_mode=ParseMode.MARKDOWN)
            return

        # Check if command is repeater itself
        if args[0].replace("/", "") in self.get_cmds():
            update.message.reply_text(
                text=f"{emo.ERROR} Repeater can't repeat itself",
                parse_mode=ParseMode.MARKDOWN)
            return

        # Set command to repeat as current message text
        update.message.text = " ".join(args)

        try:
            self._run_repeater(update, interval)
            self.tgb.db.save_rep(update, interval)
        except IntegrityError as ie:
            err = "Repeater already saved"
            update.message.reply_text(f"{emo.ERROR} {err}")
            logging.warning(f"{err} {ie}")
            return
        except Exception as e:
            update.message.reply_text(f"{emo.ERROR} {e}")
            raise e

        update.message.reply_text(text=f"{emo.CHECK} Timer is active")

    # Create job to repeatedly send command
    def _run_repeater(self, update, interval):
        args = update.message.text.split(" ")
        cmd = args[0].replace("/", "")
        plugin = None

        for plg in self.tgb.plugins:
            if cmd.lower() in plg.get_cmds():
                plugin = plg
                break

        if not plugin:
            raise Exception(f"Repeater not created. Command `/{cmd}` not found.")

        try:
            cntx = {"upd": update, "arg": args[1:], "plg": plugin}
            self.tgb.job_queue.run_repeating(self._send_msg, interval, context=cntx)
        except Exception as e:
            logging.error(repr(e))
            raise e

    # Execute repeater command
    def _send_msg(self, bot, job):
        if job.context:
            updt = job.context["upd"]
            plgn = job.context["plg"]
            args = job.context["arg"]

            if updt and plgn:
                user_id = updt.message.from_user.id
                chat_id = updt.message.chat.id
                command = updt.message.text

                active = False
                # Check if repeater still exists in DB
                for rep in self.tgb.db.read_rep(user_id, chat_id):
                    if rep[3].lower() == command.lower():
                        active = True
                        break

                if not active:
                    job.schedule_removal()
                    return

                try:
                    # Could go wrong if bot
                    # isn't authorized anymore
                    plgn.get_action(bot, updt, args=args)
                except Exception as ex:
                    logging.error(f"{ex} - {updt}")
                    self.tgb.db.delete_rep(rep)
            else:
                job.schedule_removal()
        else:
            job.schedule_removal()

    # Run all saved repeaters after all plugins loaded
    def after_plugins_loaded(self):
        if Cfg.get("database", "use_db"):
            for repeater in self.tgb.db.read_rep() or []:
                interval = repeater[4]
                update = repeater[5]

                try:
                    self._run_repeater(update, int(interval))
                except Exception as e:
                    update.message.reply_text(
                        text=f"{emo.ERROR} {e}",
                        parse_mode=ParseMode.MARKDOWN)

    def _keyboard_remove_rep(self):
        menu = self.build_menu([InlineKeyboardButton("Remove", callback_data="remove")])
        return InlineKeyboardMarkup(menu, resize_keyboard=True)

    # Callback to delete repeater
    @OpenCryptoPlugin.send_typing
    def _callback(self, bot, update):
        query = update.callback_query

        if query.data == "remove":
            text = query.message.text
            user_id = query.from_user.id

            msg_id = text.split('\n')[7]
            msg_id = msg_id.replace("(ID: ", "")
            msg_id = int(msg_id.replace(")", ""))

            for rep in self.tgb.db.read_rep(user_id):
                if msg_id == rep[0]:
                    self.tgb.db.delete_rep(msg_id)

                    index = text.rfind("\n")
                    text = f"{text[0:index]}\n"
                    text_list = text.split("\n")
                    text_list[1] = f"`{text_list[1]}`"
                    text_list[3] = f"`{text_list[3]}`"
                    text = "\n".join(text_list)

                    bot.edit_message_text(
                        text=f"{text}{emo.CANCEL} *Removed*",
                        chat_id=query.message.chat_id,
                        message_id=query.message.message_id,
                        parse_mode=ParseMode.MARKDOWN)

                    bot.answer_callback_query(query.id, text="DONE!")
                    break

    def after_plugin_loaded(self):
        # Add callback handler for removing repeaters
        self.tgb.dispatcher.add_handler(
            CallbackQueryHandler(
                self._callback,
                pattern=f"^({'|'.join(self.get_cmds())})"))

    def get_usage(self):
        return f"`/{self.get_cmds()[0]} list | i=<interval>s|m|h|d <command>`"

    def get_description(self):
        return "Repeat any command periodically"

    def get_category(self):
        return Category.BOT
