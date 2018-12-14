import opencryptobot.emoji as emo

from telegram import ParseMode
from opencryptobot.plugin import OpenCryptoPlugin
from opencryptobot.api.coingecko import CoinGecko


# TODO: Check if decimal places exist:
# https://stackoverflow.com/questions/6189956/easy-way-of-finding-decimal-places
class Value(OpenCryptoPlugin):

    def get_cmd(self):
        return "v"

    @OpenCryptoPlugin.send_typing
    @OpenCryptoPlugin.save_data
    def get_action(self, bot, update, args):
        if not args:
            update.message.reply_text(
                text=f"Usage:\n{self.get_usage()}",
                parse_mode=ParseMode.MARKDOWN)
            return

        coin = args[0].upper()

        if len(args) > 1 and self.is_number(args[1]):
            qty = float(args[1])
        else:
            update.message.reply_text(
                text=f"Usage:\n{self.get_usage()}",
                parse_mode=ParseMode.MARKDOWN)
            return

        vs_cur = str("btc,eth,usd,eur")
        if len(args) > 2:
            vs_cur = args[2]

        cg = CoinGecko()

        prices = dict()

        # Get coin ID
        for entry in cg.get_coins_list():
            if entry["symbol"].upper() == coin:
                data = cg.get_coin_by_id(entry["id"])
                prices = data["market_data"]["current_price"]
                break

        msg = str()

        for c in vs_cur.split(","):
            if c in prices:
                value = "{0:,.8f}".format(prices[c] * qty)
                msg += f"`{c.upper()}: {value}`\n"

        if msg:
            v = "{0:,}".format(int(qty) if str(qty).endswith(".0") else qty)
            msg = f"`Value of {v} {coin}`\n\n" + msg
        else:
            msg = f"{emo.ERROR} Can't retrieve data for *{coin}*"

        update.message.reply_text(
            text=msg,
            parse_mode=ParseMode.MARKDOWN)

    def get_usage(self):
        return f"`/{self.get_cmd()} <coin> <quantity> <target_currency>`"

    def get_description(self):
        return "Value for coin quantity"
