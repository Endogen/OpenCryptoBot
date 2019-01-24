import opencryptobot.emoji as emo
import opencryptobot.utils as utl

from telegram import ParseMode
from opencryptobot.ratelimit import RateLimit
from opencryptobot.api.apicache import APICache
from opencryptobot.api.coingecko import CoinGecko
from opencryptobot.plugin import OpenCryptoPlugin, Category


class Market(OpenCryptoPlugin):

    def get_cmd(self):
        return "m"

    def get_cmd_alt(self):
        return ["market"]

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
        coin_info = None

        volume = False
        if len(args) > 1:
            if args[1].lower().startswith("vol"):
                volume = True

        try:
            response = APICache.get_cg_coins_list()
        except Exception as e:
            self.handle_api_error(e, update)
            return

        # Get coin ID and data
        for entry in response:
            if entry["symbol"].upper() == coin:
                try:
                    coin_info = CoinGecko().get_coin_by_id(entry["id"])
                except Exception as e:
                    self.handle_api_error(e, update)
                    return
                break

        if not coin_info or not coin_info["tickers"]:
            update.message.reply_text(
                text=f"{emo.ERROR} No data for *{coin}*",
                parse_mode=ParseMode.MARKDOWN)
            return

        # Sort markets by volume
        if volume:
            data = sorted(
                coin_info["tickers"],
                key=lambda k: float(k["volume"]), reverse=True)

            count = len(data)
            if count > 10:
                count = 10

            msg = str()
            for i in range(count):
                vs_cur = data[i]["target"]
                exchange = data[i]["market"]["name"]
                vol_usd = data[i]["converted_volume"]["usd"]
                vol_usd = utl.format(vol_usd, decimals=2, force_length=True)

                msg += f"{exchange} - {vs_cur}\nVolume: {vol_usd} USD\n\n"

            update.message.reply_text(
                text=f"`Exchanges that trade {coin}`\n"
                     f"`Top 10 sorted by volume\n\n{msg}`",
                parse_mode=ParseMode.MARKDOWN)

        else:
            exchanges = set()
            for ticker in coin_info["tickers"]:
                exchanges.add(ticker['market']['name'])

            exchanges = "\n".join(sorted(exchanges))

            update.message.reply_text(
                text=f"`Exchanges that trade {coin}`\n\n`{exchanges}`",
                parse_mode=ParseMode.MARKDOWN)

    def get_usage(self):
        return f"`/{self.get_cmd()} <symbol> (vol)`"

    def get_description(self):
        return "Find exchanges to trade a coin"

    def get_category(self):
        return Category.GENERAL