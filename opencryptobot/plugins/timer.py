import logging
import opencryptobot.emoji as emo
import opencryptobot.utils as utl

from telegram import ParseMode
from opencryptobot.config import ConfigManager as Cfg
from opencryptobot.plugin import OpenCryptoPlugin, Category


# TODO: Better name it '/rep' repeating?
class Timer(OpenCryptoPlugin):

    def __init__(self, telegram_bot):
        super().__init__(telegram_bot)

        if not Cfg.get("database", "use_db"):
            msg = f"Plugin '{type(self).__name__}' can't be used since database is disabled"
            logging.warning(msg)

    def get_cmds(self):
        return ["timer"]

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

        t = str()
        for arg in args:
            if arg.startswith("t="):
                t = arg.replace("t=", "")
                args.remove(arg)
                break

        if not t:
            update.message.reply_text(
                text=f"{emo.ERROR} Time interval has to be provided",
                parse_mode=ParseMode.MARKDOWN)
            return

        secs = utl.get_seconds(t)

        if not secs:
            update.message.reply_text(
                text=f"{emo.ERROR} Wrong format for time interval",
                parse_mode=ParseMode.MARKDOWN)
            return

        try:
            # TODO: Find out which command to repeat and only send that string to _send_msg
            # TODO: Find instance of plugin and set it in context variable
            cntx = {"usr": update.effective_user, "cmd": update.message.text}
            self.tgb.job_queue.run_repeating(self._send_msg, secs, first=0, context=cntx)
        except Exception as e:
            logging.error(repr(e))
            return

        update.message.reply_text(
            text=f"`New timer set {emo.TOP}`",
            parse_mode=ParseMode.MARKDOWN)

    def _send_msg(self, bot, job):
        if job.context:
            usr = job.context["usr"]
            cmd = job.context["cmd"]

            if update.message:
                usr = update.message.from_user
                cmd = update.message.text
                cht = update.message.chat
            elif update.inline_query:
                usr = update.effective_user
                cmd = update.inline_query.query[:-1]
                cht = update.effective_chat
            else:
                logging.warning(f"Can't save usage - {update}")

        self.tgb.db.save_rep()

        bot.send_message(
            usr,
            f"Time task for command:\n{cmd}\n\n"
            f"{update_cmd}",
            parse_mode=ParseMode.MARKDOWN)

    def get_usage(self):
        return f"`/{self.get_cmds()[0]} t=<send command every t>s|m|h|d <command>`"

    def get_description(self):
        return "Send commands repeatedly"

    def get_category(self):
        return Category.GENERAL
