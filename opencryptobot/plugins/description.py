import opencryptobot.emoji as emo
import opencryptobot.utils as utl

from telegram import ParseMode
from opencryptobot.ratelimit import RateLimit
from opencryptobot.api.apicache import APICache
from opencryptobot.api.coingecko import CoinGecko
from opencryptobot.plugin import OpenCryptoPlugin, Category


class Description(OpenCryptoPlugin):

    def get_cmds(self):
        return ["des", "description"]

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

        try:
            response = APICache.get_cg_coins_list()
        except Exception as e:
            return self.handle_error(e, update)

        for entry in response:
            if entry["symbol"].lower() == coin.lower():
                try:
                    data = CoinGecko().get_coin_by_id(entry["id"])
                except Exception as e:
                    return self.handle_error(e, update)
                break

        if not data or not data["description"]["en"]:
            update.message.reply_text(
                text=f"{emo.INFO} No data for *{coin}*",
                parse_mode=ParseMode.MARKDOWN)
            return

        coin_desc = data["description"]["en"]

        for message in utl.split_msg(coin_desc):
            update.message.reply_text(
                text=message,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True)

    def get_usage(self):
        return f"`/{self.get_cmds()[0]} <symbol>`"

    def get_description(self):
        return "Coin description"

    def get_category(self):
        return Category.GENERAL
