import opencryptobot.emoji as emo
import opencryptobot.constants as con

from telegram import ParseMode
from opencryptobot.plugin import OpenCryptoPlugin
from opencryptobot.api.coingecko import CoinGecko


# /v btc 12 eur
class Value(OpenCryptoPlugin):

    def get_cmd(self):
        return "v"

    @OpenCryptoPlugin.send_typing
    @OpenCryptoPlugin.save_data
    def get_action(self, bot, update, args):
        if not args:
            update.message.reply_text(
                text=f"Usage:\n{self.get_usage()}",
                parse_mode=ParseMode.MARKDOWN)
            return

        coin = args[0].upper()

        qty = float()
        if len(args) > 1 and self.is_number(args[1]):
            qty = float(args[1])
        else:
            update.message.reply_text(
                text=f"Usage:\n{self.get_usage()}",
                parse_mode=ParseMode.MARKDOWN)
            return

        vs_cur = str()
        if len(args) > 2:
            vs_cur = args[2]

        cg = CoinGecko()

        coin_id = str()
        coin_name = str()

        # Get coin ID
        for entry in cg.get_coins_list():
            if entry["symbol"].upper() == coin:
                coin_name = entry["name"]
                coin_id = entry["id"]
                break

        # TODO

        update.message.reply_text(
            text=msg,
            parse_mode=ParseMode.MARKDOWN)

    def get_usage(self):
        return f"`/{self.get_cmd()} <coin> <quantity> <target_currency>`"

    def get_description(self):
        return "Value of quantity"
