import opencryptobot.emoji as emo
import opencryptobot.constants as con

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
        data = None

        for entry in cg.get_coins_list(use_cache=True):
            if entry["symbol"].lower() == coin.lower():
                data = cg.get_coin_by_id(entry["id"])
                break

        if not data or not data["description"]["en"]:
            update.message.reply_text(
                text=f"{emo.ERROR} No data for *{coin}*",
                parse_mode=ParseMode.MARKDOWN)
            return

        coin_desc = data["description"]["en"]

        if len(coin_desc) > con.MAX_TG_MSG_LEN:
            url = f"https://www.coingecko.com/en/coins/{data['id']}"
            html_link = f'...\n\n<a href="{url}">Read whole description</a>'
            coin_desc = coin_desc[:(con.MAX_TG_MSG_LEN - 27)] + html_link

        update.message.reply_text(
            text=coin_desc,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True)

    def get_usage(self):
        return f"`/{self.get_cmd()} <coin>`"

    def get_description(self):
        return "Coin description"
