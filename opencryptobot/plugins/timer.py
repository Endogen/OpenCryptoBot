import logging
import opencryptobot.emoji as emo
import opencryptobot.utils as utl

from telegram import ParseMode
from opencryptobot.config import ConfigManager as Cfg
from opencryptobot.plugin import OpenCryptoPlugin, Category


# TODO: Add reading of repeaters after bot-restart
# TODO: Create own 'update' object and always set it for 'get_action()'
# https://github.com/python-telegram-bot/python-telegram-bot/wiki/Code-snippets
class Timer(OpenCryptoPlugin):

    def __init__(self, telegram_bot):
        super().__init__(telegram_bot)

        # Check if database is enabled since this plugin needs it
        if not Cfg.get("database", "use_db"):
            msg = f"Plugin '{type(self).__name__}' can't be used since database is disabled"
            logging.warning(msg)
            return

        # Read saved repeaters
        repeaters = self.tgb.db.read_rep()

    def get_cmds(self):
        return ["re", "repeat", "timer", "rerun"]

    @OpenCryptoPlugin.save_data
    @OpenCryptoPlugin.send_typing
    def get_action(self, bot, update, args):
        if not args:
            update.message.reply_text(
                text=f"Usage:\n{self.get_usage()}",
                parse_mode=ParseMode.MARKDOWN)
            return

        if not Cfg.get("database", "use_db"):
            update.message.reply_text(
                text=f"{emo.ERROR} Database is disabled. Not possible to use command",
                parse_mode=ParseMode.MARKDOWN)
            return

        time = str()
        for arg in args:
            if arg.startswith("t="):
                time = arg.replace("t=", "")
                args.remove(arg)
                break

        if not time:
            update.message.reply_text(
                text=f"{emo.ERROR} Time interval has to be provided",
                parse_mode=ParseMode.MARKDOWN)
            return

        # In seconds
        interval = utl.get_seconds(time)

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

        # Command string to repeat
        cmd = " ".join(args)
        # Arguments without command
        args.pop(0)

        # Set command string to repeat as current message text
        update.message.text = cmd

        try:
            cntx = {"upd": update, "arg": args, "plg": plugin}
            self.tgb.job_queue.run_repeating(self._send_msg, interval, context=cntx)
        except Exception as e:
            logging.error(repr(e))
            return

        chat = update.message.chat
        user = update.message.from_user
        self.tgb.db.save_rep(user, chat, cmd, interval)

        update.message.reply_text(text=f"{emo.CHECK} Timer is active")

    # TODO: Implement
    def _run_repeater(self):
        pass

    def _send_msg(self, bot, job):
        if job.context:
            upd = job.context["upd"]
            arg = job.context["arg"]
            plg = job.context["plg"]

            if upd and arg and plg:
                plg.get_action(bot, upd, args=arg)

    def get_usage(self):
        return f"`/{self.get_cmds()[0]} t=<interval>s|m|h|d <command>`"

    def get_description(self):
        return "Send commands repeatedly"

    def get_category(self):
        return Category.GENERAL
