import opencryptobot.emoji as emo
import opencryptobot.constants as con

from telegram import ParseMode
from opencryptobot.plugin import OpenCryptoPlugin
from opencryptobot.api.coingecko import CoinGecko


class Alltimehigh(OpenCryptoPlugin):

    def get_cmd(self):
        return "ath"

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

        ath_date = str()
        ath_price = str()
        ath_change = str()

        # Get coin ID
        for entry in cg.get_coins_list():
            if entry["symbol"].lower() == coin.lower():
                coin_info = cg.get_coin_by_id(entry["id"])

                ath_price = coin_info["market_data"]["ath"]
                ath_date = coin_info["market_data"]["ath_date"]
                ath_change = coin_info["market_data"]["ath_change_percentage"]
                break

        msg = str()

        update.message.reply_text(
            text=msg,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True)

    def get_usage(self):
        return f"`/{self.get_cmd()} <coin>`"

    def get_description(self):
        return "Coin description"
