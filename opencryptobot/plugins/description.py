import opencryptobot.emoji as emo
import opencryptobot.constants as con

from telegram import ParseMode
from opencryptobot.ratelimit import RateLimit
from opencryptobot.api.apicache import APICache
from opencryptobot.api.coingecko import CoinGecko
from opencryptobot.plugin import OpenCryptoPlugin, Category


class Description(OpenCryptoPlugin):

    def get_cmd(self):
        return "des"

    @OpenCryptoPlugin.save_data
    @OpenCryptoPlugin.send_typing
    def get_action(self, bot, update, args):
        if not args:
            update.message.reply_text(
                text=f"Usage:\n{self.get_usage()}",
                parse_mode=ParseMode.MARKDOWN)
            return

        if RateLimit.limit_reached(update):
            return

        coin = args[0].upper()
        data = None

        for entry in APICache.get_cg_coins_list():
            if entry["symbol"].lower() == coin.lower():
                data = CoinGecko().get_coin_by_id(entry["id"])
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

    def get_category(self):
        return Category.GENERAL
