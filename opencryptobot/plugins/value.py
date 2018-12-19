import opencryptobot.emoji as emo

from telegram import ParseMode
from opencryptobot.api.coingecko import CoinGecko
from opencryptobot.plugin import OpenCryptoPlugin, Category


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
            qty = args[1]
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
        for entry in cg.get_coins_list(use_cache=True):
            if entry["symbol"].upper() == coin:
                data = cg.get_coin_by_id(entry["id"])
                prices = data["market_data"]["current_price"]
                break

        try:
            qty_float = float(qty)
        except Exception:
            update.message.reply_text(
                text=f"{emo.ERROR} Quantity '{qty}' not valid",
                parse_mode=ParseMode.MARKDOWN)
            return

        msg = str()

        for c in vs_cur.split(","):
            if c in prices:
                value = self.format(prices[c] * qty_float)
                msg += f"`{c.upper()}: {value}`\n"

        if msg:
            msg = f"`Value of {qty} {coin}`\n\n" + msg
        else:
            msg = f"{emo.ERROR} Can't retrieve data for *{coin}*"

        update.message.reply_text(
            text=msg,
            parse_mode=ParseMode.MARKDOWN)

    def get_usage(self):
        return f"`/{self.get_cmd()} <coin> <quantity> (<target_currency>)`"

    def get_description(self):
        return "Value of coin quantity"

    def get_category(self):
        return Category.PRICE
