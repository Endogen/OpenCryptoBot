import decimal
import opencryptobot.emoji as emo
import opencryptobot.utils as utl

from telegram import ParseMode
from opencryptobot.ratelimit import RateLimit
from opencryptobot.api.apicache import APICache
from opencryptobot.api.coingecko import CoinGecko
from opencryptobot.plugin import OpenCryptoPlugin, Category


class Price(OpenCryptoPlugin):

    def get_cmd(self):
        return "p"

    def get_cmd_alt(self):
        return ["price"]

    @OpenCryptoPlugin.save_data
    @OpenCryptoPlugin.send_typing
    def get_action(self, bot, update, args):
        vs_cur = str()

        if not args:
            if update.message:
                update.message.reply_text(
                    text=f"Usage:\n{self.get_usage(bot.name)}",
                    parse_mode=ParseMode.MARKDOWN)
            return

        # Coin name
        if "-" in args[0]:
            pair = args[0].split("-", 1)
            vs_cur = pair[0].upper()
            coin = pair[1].upper()
        else:
            coin = args[0].upper()

        # Exchange name
        exchange = str()
        if len(args) > 1:
            exchange = args[1]

        try:
            response = APICache.get_cg_coins_list()
        except Exception as e:
            self.handle_api_error(e, update)
            return

        # Get coin ID and name
        coin_id = str()
        for entry in response:
            if entry["symbol"].upper() == coin:
                coin_id = entry["id"]
                break

        if RateLimit.limit_reached(update):
            return

        cg = CoinGecko()
        msg = str()

        if exchange:
            try:
                result = cg.get_coin_by_id(coin_id)
            except Exception as e:
                self.handle_api_error(e, update)
                return

            if result:
                vs_list = list()

                if vs_cur:
                    vs_list = vs_cur.split(",")

                for ticker in result["tickers"]:
                    if ticker["market"]["name"].upper() == exchange.upper():
                        base_coin = ticker["target"]
                        if vs_list:
                            if base_coin in vs_list:
                                price = utl.format(ticker["last"], force_length=True)
                                msg += f"`{base_coin}: {price}`\n"
                        else:
                            price = utl.format(ticker["last"], force_length=True)
                            msg += f"`{base_coin}: {price}`\n"
        else:
            if not vs_cur:
                if coin == "BTC":
                    vs_cur = "ETH,USD,EUR"
                elif coin == "ETH":
                    vs_cur = "BTC,USD,EUR"
                else:
                    vs_cur = "BTC,ETH,USD,EUR"

            try:
                result = cg.get_simple_price(coin_id, vs_cur)
            except Exception as e:
                self.handle_api_error(e, update)
                return

            if result:
                fiat_list = APICache.get_cg_fiat_list()
                for symbol, price in next(iter(result.values())).items():
                    if symbol in fiat_list:
                        if decimal.Decimal(str(price)).as_tuple().exponent > -3:
                            price = utl.format(price, decimals=2, force_length=True)
                        else:
                            price = utl.format(price, force_length=True)
                    else:
                        price = utl.format(price, force_length=True)

                    msg += f"`{symbol.upper()}: {price}`\n"

        if msg:
            if exchange:
                msg = f"`Price of {coin} on {exchange.capitalize()}`\n\n" + msg
            else:
                msg = f"`Price of {coin}`\n\n" + msg
        else:
            msg = f"{emo.ERROR} Can't retrieve data for *{coin}*"

        if update.message:
            update.message.reply_text(
                text=msg,
                parse_mode=ParseMode.MARKDOWN)
        else:
            return msg

    def get_usage(self, bot_name):
        return f"`" \
               f"/{self.get_cmd()} <coin>\n" \
               f"/{self.get_cmd()} <vs coin>-<coin>\n" \
               f"{bot_name} /{self.get_cmd()} <coin>.\n" \
               f"{bot_name} /{self.get_cmd()} <vs coin>-<coin>." \
               f"`"

    def get_description(self):
        return "Coin price"

    def get_category(self):
        return Category.PRICE

    def inline_mode(self):
        return True
