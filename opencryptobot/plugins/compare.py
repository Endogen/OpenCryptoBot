import time
import opencryptobot.emoji as emo

from telegram import ParseMode
from opencryptobot.plugin import OpenCryptoPlugin, Category


class Compare(OpenCryptoPlugin):

    BASE_URL = "https://coinlib.io/compare/"

    def get_cmds(self):
        return ["comp", "compare"]

    @OpenCryptoPlugin.save_data
    @OpenCryptoPlugin.send_typing
    def get_action(self, bot, update, args):
        if not args:
            update.message.reply_text(
                text=f"Usage:\n{self.get_usage()}",
                parse_mode=ParseMode.MARKDOWN)
            return

        if len(args) == 1:
            update.message.reply_text(
                text=f"{emo.ERROR} Enter at least 2 coins to compare them",
                parse_mode=ParseMode.MARKDOWN)
            return

        if len(args) > 8:
            update.message.reply_text(
                text=f"{emo.ERROR} Not possible to compare more then 8 coins",
                parse_mode=ParseMode.MARKDOWN)
            return

        y, m, d = time.strftime("%Y-%m-%d").split("-")

        if int(m) - 1 < 1:
            y = str(int(y) - 1)
        else:
            m = str(int(m) - 1)
        if len(m) == 1:
            m = f"0{m}"
        if len(d) == 1:
            d = f"0{d}"

        url = f"{self.BASE_URL}{y}-{m}-{d}/"

        for symbol in args:
            url += f"{symbol.upper()}/"

        title = f"Compare {' & '.join(args).upper()}"
        msg = f"[{title}]({url})"

        update.message.reply_text(
            text=msg,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True)

    def get_usage(self):
        return f"`/{self.get_cmds()[0]} <symbol> <symbol> ...`"

    def get_description(self):
        return "Compare coins"

    def get_category(self):
        return Category.GENERAL
