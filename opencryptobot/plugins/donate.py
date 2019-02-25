import os
import opencryptobot.constants as con

from telegram import ParseMode
from opencryptobot.plugin import OpenCryptoPlugin, Category


class Donate(OpenCryptoPlugin):

    def get_cmds(self):
        return ["donate", "donateBTC", "donateBCH", "donateETH", "donateXMR"]

    @OpenCryptoPlugin.save_data
    @OpenCryptoPlugin.send_typing
    def get_action(self, bot, update, args):
        # Donate
        if update.message.text == f"/{self.get_cmds()[0]}":
            msg = str()
            for cmd in self.get_cmds()[1:]:
                msg += f"/{cmd}\n"

            update.message.reply_text(msg)
            return

        # BTC
        if update.message.text == f"/{self.get_cmds()[1]}":
            qr_code = self._get_qr_code("BTC")
            if qr_code:
                update.message.reply_photo(
                    photo=qr_code,
                    caption="Bitcoin (BTC)",
                    parse_mode=ParseMode.MARKDOWN)
            return

        # BCH
        if update.message.text == f"/{self.get_cmds()[2]}":
            qr_code = self._get_qr_code("BCH")
            if qr_code:
                update.message.reply_photo(
                    photo=qr_code,
                    caption="Bitcoin Cash (BCH)",
                    parse_mode=ParseMode.MARKDOWN)
            return

        # ETH
        if update.message.text == f"/{self.get_cmds()[3]}":
            qr_code = self._get_qr_code("ETH")
            if qr_code:
                update.message.reply_photo(
                    photo=qr_code,
                    caption="Ethereum (ETH)",
                    parse_mode=ParseMode.MARKDOWN)
            return

        # XMR
        if update.message.text == f"/{self.get_cmds()[4]}":
            qr_code = self._get_qr_code("XMR")
            if qr_code:
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

    def _get_qr_code(self, symbol):
        try:
            return open(os.path.join(con.RES_DIR, f"{symbol}.png"), "rb")
        except Exception:
            return None
