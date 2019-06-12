import opencryptobot.emoji as emo
import opencryptobot.utils as utl

from telegram import ParseMode
from opencryptobot.ratelimit import RateLimit
from opencryptobot.api.coindata import CoinData
from opencryptobot.plugin import OpenCryptoPlugin, Category, Keyword


class Best(OpenCryptoPlugin):

    DESC_LEN = 25

    def get_cmds(self):
        return ["best"]

    @OpenCryptoPlugin.save_data
    @OpenCryptoPlugin.send_typing
    def get_action(self, bot, update, args):
        keywords = utl.get_kw(args)
        arg_list = utl.del_kw(args)

        if arg_list:
            t = arg_list[0].lower()
            if not t == "hour" and not t == "day":
                if not keywords.get(Keyword.INLINE):
                    update.message.reply_text(
                        text=f"{emo.ERROR} First argument has to be `day` or `hour`",
                        parse_mode=ParseMode.MARKDOWN)
                return

        if len(arg_list) > 1:
            entries = arg_list[1]
            if not entries.isnumeric():
                if not keywords.get(Keyword.INLINE):
                    update.message.reply_text(
                        text=f"{emo.ERROR} Second argument (# of positions "
                             f"to display) has to be a number",
                        parse_mode=ParseMode.MARKDOWN)
                return

        if len(arg_list) > 2:
            entries = arg_list[2]
            if not entries.isnumeric():
                if not keywords.get(Keyword.INLINE):
                    update.message.reply_text(
                        text=f"{emo.ERROR} Third argument (min. volume) "
                             f"has to be a number",
                        parse_mode=ParseMode.MARKDOWN)
                return

        if RateLimit.limit_reached(update):
            return

        period = CoinData.HOUR
        volume = None
        entries = 10

        if arg_list:
            # Period
            if arg_list[0].lower() == "hour":
                period = CoinData.HOUR
            elif arg_list[0].lower() == "day":
                period = CoinData.DAY
            else:
                period = CoinData.HOUR

            # Entries
            if len(arg_list) > 1 and arg_list[1].isnumeric():
                entries = int(arg_list[1])

            # Volume
            if len(arg_list) > 2 and arg_list[2].isnumeric():
                volume = int(arg_list[2])

        try:
            best = CoinData().get_movers(
                CoinData.BEST,
                period=period,
                entries=entries,
                volume=volume)
        except Exception as e:
            return self.handle_error(e, update)

        if not best:
            if not keywords.get(Keyword.INLINE):
                update.message.reply_text(
                    text=f"{emo.INFO} No matching data found",
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

            change = utl.format(change, decimals=2, force_length=True)
            change = "{1:>{0}}".format(self.DESC_LEN + 9 - len(desc), change)
            msg += f"`{desc}{change}%`\n"

        vol = str()
        if volume:
            vol = f" (vol > {utl.format(volume)})"

        msg = f"`Best movers 1{period.lower()[:1]}{vol}\n\n`{msg}"

        if keywords.get(Keyword.INLINE):
            return msg

        self.send_msg(msg, update, keywords)

    def get_usage(self):
        return f"`/{self.get_cmds()[0]} hour | day (<# of entries>) (<min. volume>)`"

    def get_description(self):
        return "Best movers for hour or day"

    def get_category(self):
        return Category.PRICE

    def inline_mode(self):
        return True
