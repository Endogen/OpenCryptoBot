import opencryptobot.emoji as emo
import opencryptobot.utils as utl

from telegram import ParseMode
from opencryptobot.ratelimit import RateLimit
from opencryptobot.api.apicache import APICache
from opencryptobot.api.coingecko import CoinGecko
from opencryptobot.plugin import OpenCryptoPlugin, Category


class Change(OpenCryptoPlugin):

    def get_cmds(self):
        return ["ch", "change"]

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

        vs_cur = "usd"

        if "-" in args[0]:
            pair = args[0].split("-", 1)
            vs_cur = pair[1].lower()
            coin = pair[0].upper()
        else:
            coin = args[0].upper()

        data = None

        try:
            response = APICache.get_cg_coins_list()
        except Exception as e:
            return self.handle_error(e, update)

        # Get coin ID and data
        for entry in response:
            if entry["symbol"].upper() == coin:
                try:
                    data = CoinGecko().get_coin_by_id(entry["id"])
                except Exception as e:
                    return self.handle_error(e, update)
                break

        if not data:
            update.message.reply_text(
                text=f"{emo.INFO} No data for *{coin}*",
                parse_mode=ParseMode.MARKDOWN)
            return

        name = data["name"]
        symbol = data["symbol"].upper()

        if data["market_data"]["price_change_percentage_1h_in_currency"]:
            c_1h = data["market_data"]["price_change_percentage_1h_in_currency"][vs_cur]
            c1h = utl.format(float(c_1h), decimals=2, force_length=True)
            h1 = "{:>10}".format(f"{c1h}%")
        else:
            h1 = "{:>10}".format("N/A")

        if data["market_data"]["price_change_percentage_24h_in_currency"]:
            c_1d = data["market_data"]["price_change_percentage_24h_in_currency"][vs_cur]
            c1d = utl.format(float(c_1d), decimals=2, force_length=True)
            d1 = "{:>10}".format(f"{c1d}%")
        else:
            d1 = "{:>10}".format("N/A")

        if data["market_data"]["price_change_percentage_7d_in_currency"]:
            c_1w = data["market_data"]["price_change_percentage_7d_in_currency"][vs_cur]
            c1w = utl.format(float(c_1w), decimals=2, force_length=True)
            w1 = "{:>10}".format(f"{c1w}%")
        else:
            w1 = "{:>10}".format("N/A")

        if data["market_data"]["price_change_percentage_30d_in_currency"]:
            c_1m = data["market_data"]["price_change_percentage_30d_in_currency"][vs_cur]
            c1m = utl.format(float(c_1m), decimals=2, force_length=True)
            m1 = "{:>10}".format(f"{c1m}%")
        else:
            m1 = "{:>10}".format("N/A")

        if data["market_data"]["price_change_percentage_1y_in_currency"]:
            c_1y = data["market_data"]["price_change_percentage_1y_in_currency"]["usd"]
            c1y = utl.format(float(c_1y), decimals=2, force_length=True)
            y1 = "{:>10}".format(f"{c1y}%")
        else:
            y1 = "{:>10}".format("N/A")

        update.message.reply_text(
            text=f"`"
                 f"{name} ({symbol}) in {vs_cur.upper()}\n\n"
                 f"Hour  {h1}\n"
                 f"Day   {d1}\n"
                 f"Week  {w1}\n"
                 f"Month {m1}\n"
                 f"Year  {y1}\n\n"
                 f"`",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True)

    def get_usage(self):
        return f"`/{self.get_cmds()[0]} <symbol>(-<target symbol>)`"

    def get_description(self):
        return "Price change over time"

    def get_category(self):
        return Category.PRICE
