import opencryptobot.emoji as emo
import opencryptobot.utils as utl

from telegram import ParseMode
from opencryptobot.ratelimit import RateLimit
from opencryptobot.api.coingecko import CoinGecko
from opencryptobot.plugin import OpenCryptoPlugin, Category


class Top(OpenCryptoPlugin):

    def get_cmds(self):
        return ["top"]

    @OpenCryptoPlugin.save_data
    @OpenCryptoPlugin.send_typing
    def get_action(self, bot, update, args):
        base_cur = "USD"
        fiat_symbol = "$"

        if args:
            base_cur = args[0].upper()
            if base_cur == "EUR":
                fiat_symbol = "€"

        if RateLimit.limit_reached(update):
            return

        try:
            market = CoinGecko().get_coins_markets(
                    base_cur.lower(),
                    per_page=30,
                    page=1,
                    order="market_cap_desc",
                    sparkline=False,
                    price_change_percentage=False)
        except Exception as e:
            return self.handle_error(e, update)

        msg = str()

        if market:
            for i in range(30):
                rank = market[i]['market_cap_rank']
                symbol = market[i]['symbol'].upper()
                name = market[i]['name']

                price = market[i]['current_price']
                price = utl.format(price, decimals=4, symbol=base_cur)

                if base_cur == "EUR":
                    price = f"{price} {fiat_symbol}"
                    mcap = f"{utl.format(market[i]['market_cap'])}{fiat_symbol}"
                    vol = f"{utl.format(market[i]['total_volume'])}{fiat_symbol}"
                elif base_cur == "USD":
                    price = f"{fiat_symbol}{price}"
                    mcap = f"{fiat_symbol}{utl.format(market[i]['market_cap'])}"
                    vol = f"{fiat_symbol}{utl.format(market[i]['total_volume'])}"
                else:
                    price = f"{price}"
                    mcap = f"{utl.format(market[i]['market_cap'])}"
                    vol = f"{utl.format(market[i]['total_volume'])}"

                msg += f"{rank}. *{symbol}* ({name}) - {price}\n" \
                       f"` M.Cap.: {mcap}`\n" \
                       f"` Volume: {vol}`\n"

        if msg:
            msg = f"*Top 30 Coins by Market Cap in {base_cur}*\n\n {msg}"
        else:
            msg = f"{emo.ERROR} Can't retrieve toplist"

        update.message.reply_text(
            text=msg,
            parse_mode=ParseMode.MARKDOWN)

    def get_usage(self):
        return f"`/{self.get_cmds()[0]} (<target symbol>)`"

    def get_description(self):
        return "List top 30 coins"

    def get_category(self):
        return Category.GENERAL
