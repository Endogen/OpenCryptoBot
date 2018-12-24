import opencryptobot.emoji as emo

from telegram import ParseMode
from opencryptobot.utils import format
from opencryptobot.api.coindata import CoinData
from opencryptobot.plugin import OpenCryptoPlugin, Category


class Worst(OpenCryptoPlugin):

    DESC_LEN = 25

    def get_cmd(self):
        return "worst"

    @OpenCryptoPlugin.send_typing
    @OpenCryptoPlugin.save_data
    def get_action(self, bot, update, args):
        period = CoinData.HOUR
        volume = None
        entries = 10

        if args:
            # Period
            if args[0].lower() == "hour":
                period = CoinData.HOUR
            elif args[0].lower() == "day":
                period = CoinData.DAY
            else:
                period = CoinData.HOUR

            # Entries
            if len(args) > 1 and args[1].isnumeric():
                entries = int(args[1])

            # Volume
            if len(args) > 2 and args[2].isnumeric():
                volume = int(args[2])

        best = CoinData().get_movers(
            CoinData.WORST,
            period=period,
            entries=entries,
            volume=volume)

        if not best:
            update.message.reply_text(
                text=f"{emo.ERROR} No matching data found",
                parse_mode=ParseMode.MARKDOWN)
            return

        msg = str()

        for coin in best:
            name = coin["Name"]
            symbol = coin["Symbol"]
            desc = f"{name} ({symbol})"

            if len(desc) > self.DESC_LEN:
                desc = f"{desc[:self.DESC_LEN-3]}..."

            if period == CoinData.HOUR:
                change = coin["Change_1h"]
            else:
                change = coin["Change_24h"]

            change = format(change, decimals=2, force_length=True)
            change = "{1:>{0}}".format(self.DESC_LEN + 9 - len(desc), change)
            msg += f"`{desc}{change}%`\n"

        vol = str()
        if volume:
            vol = f" (vol > {format(volume)})"

        update.message.reply_text(
            text=f"`Worst movers 1{period.lower()[:1]}{vol}\n\n`" + msg,
            parse_mode=ParseMode.MARKDOWN)

    def get_usage(self):
        return f"`/{self.get_cmd()} 'hour' or 'day' (<# of entries> <min. volume>)`"

    def get_description(self):
        return "Worst movers for hour or day"

    def get_category(self):
        return Category.PRICE
