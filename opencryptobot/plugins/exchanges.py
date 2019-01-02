import opencryptobot.emoji as emo
import opencryptobot.constants as con

from telegram import ParseMode
from opencryptobot.api.apicache import APICache
from opencryptobot.api.coingecko import CoinGecko
from opencryptobot.plugin import OpenCryptoPlugin, Category


# TODO: Complete implementation
class Exchanges(OpenCryptoPlugin):

    def get_cmd(self):
        return "ex"

    @OpenCryptoPlugin.send_typing
    @OpenCryptoPlugin.save_data
    def get_action(self, bot, update, args):
        if not args:
            update.message.reply_text(
                text=f"Usage:\n{self.get_usage()}",
                parse_mode=ParseMode.MARKDOWN)
            return

        coin = args[0].upper()
        data = None

        for entry in APICache.get_cg_coins_list():
            if entry["symbol"].lower() == coin.lower():
                data = CoinGecko().get_coin_by_id(entry["id"])
                break

        # TODO

        update.message.reply_text(
            text=msg,
            parse_mode=ParseMode.MARKDOWN)

    def get_usage(self):
        return f"`/{self.get_cmd()} <exchange>`"

    def get_description(self):
        return "Exchange details"

    def get_category(self):
        return Category.GENERAL
