import logging
import opencryptobot.emoji as emo
import opencryptobot.utils as utl

from telegram import ParseMode
from opencryptobot.config import ConfigManager as Cfg
from opencryptobot.plugin import OpenCryptoPlugin, Category


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

        if not args:
            update.message.reply_text(
                text=f"Usage:\n{self.get_usage()}",
                parse_mode=ParseMode.MARKDOWN)
            return

        # Extract time interval
        interval = str()
        for arg in args:
            if arg.startswith("i="):
                interval = arg.replace("i=", "")
                args.remove(arg)
                break

        if not interval:
            update.message.reply_text(
                text=f"{emo.ERROR} Time interval has to be provided",
                parse_mode=ParseMode.MARKDOWN)
            return

        # In seconds
        interval = utl.get_seconds(interval)

        if not interval:
            update.message.reply_text(
                text=f"{emo.ERROR} Wrong format for time interval",
                parse_mode=ParseMode.MARKDOWN)
            return

        if not args:
            update.message.reply_text(
                text=f"{emo.ERROR} No command to repeat",
                parse_mode=ParseMode.MARKDOWN)
            return

        if not update.message:
            update.message.reply_text(
                text=f"{emo.ERROR} Message is empty",
                parse_mode=ParseMode.MARKDOWN)
            return

        command = args[0].replace("/", "")
        plugin = None

        for plg in self.tgb.plugins:
            if command in plg.get_cmds():
                plugin = plg
                break

        if not plugin:
            update.message.reply_text(
                text=f"{emo.ERROR} Command `/{command}` does not exist",
                parse_mode=ParseMode.MARKDOWN)
            return

        # Set command to repeat as current message text
        update.message.text = " ".join(args)

        try:
            self._run_repeater(update, interval)
            self.tgb.db.save_rep(update, interval)
        except Exception as e:
            update.message.reply_text(text=f"{emo.ERROR} {e}")
            raise e

        update.message.reply_text(text=f"{emo.CHECK} Timer is active")

    def _run_repeater(self, update, interval):
        args = update.message.text.split(" ")
        command = args[0].replace("/", "")
        plugin = None

        for plg in self.tgb.plugins:
            if command in plg.get_cmds():
                plugin = plg
                break

        if not plugin:
            raise Exception(f"Can not create repeater. Command `/{command}` not available.")

        try:
            cntx = {"upd": update, "arg": args[1:], "plg": plugin}
            self.tgb.job_queue.run_repeating(self._send_msg, interval, context=cntx)
        except Exception as e:
            logging.error(repr(e))

    def _send_msg(self, bot, job):
        if job.context:
            upd = job.context["upd"]
            arg = job.context["arg"]
            plg = job.context["plg"]

            if upd and arg and plg:
                plg.get_action(bot, upd, args=arg)

    def after_plugins_loaded(self):
        for repeater in self.tgb.db.read_rep() or []:
            update = repeater[4]
            interval = repeater[3]

            try:
                self._run_repeater(update, int(interval))
            except Exception as e:
                update.message.reply_text(text=f"{emo.ERROR} {e}")

    def get_usage(self):
        return f"`/{self.get_cmds()[0]} i=<interval>s|m|h|d <command>`"

    def get_description(self):
        return "Send commands repeatedly"

    def get_category(self):
        return Category.GENERAL
