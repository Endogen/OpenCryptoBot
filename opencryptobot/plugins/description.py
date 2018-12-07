import opencryptobot.emoji as emo

from telegram import ParseMode
from opencryptobot.plugin import OpenCryptoPlugin
from opencryptobot.api.coingecko import CoinGecko


class Description(OpenCryptoPlugin):

    def get_cmd(self):
        return "des"

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

        # Get coin ID
        for entry in cg.get_coins_list():
            if entry["symbol"].lower() == coin.lower():
                # Get coin info
                coin_info = cg.get_coin_by_id(entry["id"])
                break

        if not coin_info or not coin_info["description"]["en"]:
            update.message.reply_text(
                text=f"{emo.ERROR} No data for *{coin}*",
                parse_mode=ParseMode.MARKDOWN)
            return

        update.message.reply_text(
            text=coin_info["description"]["en"],
            disable_web_page_preview=True,
            parse_mode=ParseMode.HTML)

    def get_usage(self):
        return f"`/{self.get_cmd()} <coin>`"

    def get_description(self):
        return "Coin description"
