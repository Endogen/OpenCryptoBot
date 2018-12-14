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

        coin_id = str()

        # Get coin ID
        for entry in cg.get_coins_list():
            if entry["symbol"].upper() == coin:
                coin_id = entry["id"]
                break

        data = cg.get_coin_by_id(coin_id)

        msg = str()

        prices = data["market_data"]["current_price"]
        for c in vs_cur.split(","):
            if c in prices:
                value = "{0:.8f}".format(prices[c] * qty)
                msg += f"`{c.upper()}: {value}`\n"

        if not msg:
            msg = f"{emo.ERROR} Can't retrieve data for *{coin}*"
        else:
            msg = f"Value of {str(qty)} {coin}\n" + msg

        update.message.reply_text(
            text=msg,
            parse_mode=ParseMode.MARKDOWN)

    def get_usage(self):
        return f"`/{self.get_cmd()} <coin> <quantity> <target_currency>`"

    def get_description(self):
        return "Value of quantity"
