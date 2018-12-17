import datetime
import opencryptobot.emoji as emo

from datetime import date
from telegram import ParseMode
from opencryptobot.api.coingecko import CoinGecko
from opencryptobot.plugin import OpenCryptoPlugin, Category


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

        vs_cur = "usd"
        if len(args) > 1:
            vs_cur = args[1]

        cg = CoinGecko()

        ath_date = str()
        ath_price = str()
        cur_price = str()
        ath_change = str()

        # Get coin ID
        for entry in cg.get_coins_list(use_cache=True):
            if entry["symbol"].lower() == coin.lower():
                coin_info = cg.get_coin_by_id(entry["id"])

                cur_price = coin_info["market_data"]["current_price"]
                ath_price = coin_info["market_data"]["ath"]
                ath_date = coin_info["market_data"]["ath_date"]
                ath_change = coin_info["market_data"]["ath_change_percentage"]
                break

        msg = str()

        for c in vs_cur.split(","):
            if c in ath_price:
                ath_p = self.format(ath_price[c])
                cur_p = self.format(cur_price[c], template=ath_p)
                change = "{0:.2f}".format(ath_change[c])

                date_time = ath_date[c]
                date_ath = date_time[:10]
                date_list = date_ath.split("-")
                y = int(date_list[0])
                m = int(date_list[1])
                d = int(date_list[2])

                ath = date(y, m, d)
                now = datetime.date.today()

                ath_p_str = f"Price ATH: {ath_p} {c.upper()}\n"
                cur_p_str = f"Price now: {cur_p.rjust(len(ath_p))} {c.upper()}\n"

                msg += f"`" \
                       f"{date_ath} ({(now - ath).days} days ago)\n" \
                       f"{ath_p_str}" \
                       f"{cur_p_str}" \
                       f"Change: {change}%\n\n" \
                       f"`"

        if msg:
            msg = f"`All-Time High for {coin}`\n\n" + msg
        else:
            msg = f"{emo.ERROR} Can't retrieve data for *{coin}*"

        update.message.reply_text(
            text=msg,
            parse_mode=ParseMode.MARKDOWN)

    def get_usage(self):
        return f"`/{self.get_cmd()} <coin> (<in currency>)`"

    def get_description(self):
        return "All time high price for coin"

    def get_category(self):
        return Category.PRICE
