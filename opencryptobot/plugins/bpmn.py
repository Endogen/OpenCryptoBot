import os
import opencryptobot.emoji as emo
import opencryptobot.constants as con

from telegram import ParseMode
from opencryptobot.telegrambot import TelegramBot
from opencryptobot.plugin import OpenCryptoPlugin, Category


class Bpmn(OpenCryptoPlugin):

    def get_cmd(self):
        return "bpmn"

    @OpenCryptoPlugin.save_data
    @OpenCryptoPlugin.send_typing
    def get_action(self, bot, update, args):
        if not args:
            update.message.reply_text(
                text=f"Usage:\n{self.get_usage()}",
                parse_mode=ParseMode.MARKDOWN)
            return

        cmd = args[0].replace("/", "").lower()

        cmd_found = False
        for plgn in self.tgb.plugins:
            if plgn.get_cmd() == cmd or cmd in plgn.get_cmd_alt():
                cmd = plgn.get_cmd()
                cmd_found = True

        if not cmd_found:
            msg = f"{emo.ERROR} Command `/{cmd}` doesn't exist"
            update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)
            return

        try:
            bpmn = open(os.path.join(con.BPMN_DIR, f"{cmd}.png"), "rb")
        except Exception:
            msg = f"{emo.ERROR} No BPMN diagram found for `/{cmd}`"
            update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)
            return

        update.message.reply_photo(
            photo=bpmn,
            caption=f"Process flow for `/{cmd}` command",
            parse_mode=ParseMode.MARKDOWN)

    def get_usage(self):
        return f"`/{self.get_cmd()} <command>`"

    def get_description(self):
        return "BPMN diagram for a command"

    def get_category(self):
        return Category.BOT
