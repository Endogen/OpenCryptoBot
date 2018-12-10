import opencryptobot.emoji as emo

from telegram import ParseMode
from opencryptobot.plugin import OpenCryptoPlugin
from opencryptobot.api.coingecko import CoinGecko


class Wheretobuy(OpenCryptoPlugin):

    def get_cmd(self):
        return "buy"

    @OpenCryptoPlugin.send_typing
    @OpenCryptoPlugin.save_data
    def get_action(self, bot, update, args):
        if not args:
            update.message.reply_text(
                text=f"Usage:\n{self.get_usage()}",
                parse_mode=ParseMode.MARKDOWN)
            return

        coin = args[0].upper()

        cg = CoinGecko()
        coin_info = None

        # Get coin ID and data
        for entry in cg.get_coins_list():
            if entry["symbol"].upper() == coin:
                coin_info = cg.get_coin_by_id(entry["id"])
                break

        if not coin_info or not coin_info["tickers"]:
            update.message.reply_text(
                text=f"{emo.ERROR} No data for *{coin}*",
                parse_mode=ParseMode.MARKDOWN)
            return

        markets = set()
        for ticker in coin_info["tickers"]:
            markets.add(ticker['market']['name'])

        markets = "\n".join(sorted(markets))

        update.message.reply_text(
            text=f"Exchanges that trade *{coin}*\n\n`{markets}`",
            parse_mode=ParseMode.MARKDOWN)

    def get_usage(self):
        return f"`/{self.get_cmd()} <coin>`"

    def get_description(self):
        return "Where to buy a coin"
