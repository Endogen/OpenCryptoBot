import os
import opencryptobot.constants as con

from telegram import ParseMode
from opencryptobot.plugin import OpenCryptoPlugin, Category


class Donate(OpenCryptoPlugin):

    BTC = "BTC.png"
    BCH = "BCH.png"
    ETH = "ETH.png"
    XMR = "XMR.png"

    def get_cmd(self):
        return "donate"

    def get_cmd_alt(self):
        return ["donateBTC", "donateBCH", "donateETH", "donateXMR"]

    @OpenCryptoPlugin.send_typing
    @OpenCryptoPlugin.save_data
    def get_action(self, bot, update, args):
        # Donate
        if update.message.text == f"/{self.get_cmd()}":
            msg = str()
            for cmd in self.get_cmd_alt():
                msg += f"/{cmd}\n"

            update.message.reply_text(msg)
            return

        # BTC
        if update.message.text == f"/{self.get_cmd_alt()[0]}":
            qr_code = open(os.path.join(con.RES_DIR, self.BTC), "rb")
            update.message.reply_photo(
                photo=qr_code,
                caption="Bitcoin (BTC)",
                parse_mode=ParseMode.MARKDOWN)

            return

        # BCH
        if update.message.text == f"/{self.get_cmd_alt()[1]}":
            qr_code = open(os.path.join(con.RES_DIR, self.BCH), "rb")
            update.message.reply_photo(
                photo=qr_code,
                caption="Bitcoin Cash (BCH)",
                parse_mode=ParseMode.MARKDOWN)

            return

        # ETH
        if update.message.text == f"/{self.get_cmd_alt()[2]}":
            qr_code = open(os.path.join(con.RES_DIR, self.ETH), "rb")
            update.message.reply_photo(
                photo=qr_code,
                caption="Ethereum (ETH)",
                parse_mode=ParseMode.MARKDOWN)

            return

        # XMR
        if update.message.text == f"/{self.get_cmd_alt()[3]}":
            qr_code = open(os.path.join(con.RES_DIR, self.XMR), "rb")
            update.message.reply_photo(
                photo=qr_code,
                caption="Monero (XMR)",
                parse_mode=ParseMode.MARKDOWN)

            return

    def get_usage(self):
        return None

    def get_description(self):
        return None

    def get_category(self):
        return Category.BOT
