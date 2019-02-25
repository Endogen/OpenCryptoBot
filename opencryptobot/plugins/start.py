import os
import opencryptobot.constants as con

from telegram import ParseMode
from opencryptobot.plugin import OpenCryptoPlugin


class Start(OpenCryptoPlugin):

    START_FILENAME = "start.md"

    def get_cmds(self):
        return ["start"]

    def get_action(self, bot, update, args):
        about_file = os.path.join(con.RES_DIR, self.START_FILENAME)
        with open(about_file, "r", encoding="utf8") as file:
            content = file.readlines()

        update.message.reply_text(
            text="".join(content),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True)

    def get_usage(self):
        return None

    def get_description(self):
        return None

    def get_category(self):
        return None
