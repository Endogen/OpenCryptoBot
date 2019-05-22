import opencryptobot.emoji as emo
import opencryptobot.utils as utl

from telegram import ParseMode
from opencryptobot.ratelimit import RateLimit
from opencryptobot.api.apicache import APICache
from opencryptobot.api.coingecko import CoinGecko
from opencryptobot.plugin import OpenCryptoPlugin, Category


class Volume(OpenCryptoPlugin):

    def get_cmds(self):
        return ["vol", "volume"]

    @OpenCryptoPlugin.save_data
    @OpenCryptoPlugin.send_typing
    def get_action(self, bot, update, args):
        if not args:
            update.message.reply_text(
                text=f"Usage:\n{self.get_usage()}",
                parse_mode=ParseMode.MARKDOWN)
            return

        msg = str()
        top = str()
        coin = str()
        vs_cur = "usd"

        if args[0].lower().startswith("top="):
            top = args[0][4:]

            if not top.isnumeric():
                update.message.reply_text(
                    text=f"{emo.ERROR} Value of `top` has to be a number",
                    parse_mode=ParseMode.MARKDOWN)
                return
            if int(top) > 100:
                update.message.reply_text(
                    text=f"{emo.ERROR} Max value for `top` is `100`",
                    parse_mode=ParseMode.MARKDOWN)
                return
        else:
            if "-" in args[0]:
                pair = args[0].split("-", 1)
                vs_cur = pair[1].lower()
                coin = pair[0].lower()
            else:
                coin = args[0].lower()

        if RateLimit.limit_reached(update):
            return

        # ---------- TOP VOLUME ----------

        if top:
            try:
                data = CoinGecko().get_coins_markets(
                    vs_cur,
                    per_page=top,
                    page=1,
                    order="volume_desc",
                    sparkline=False)
            except Exception as e:
                return self.handle_error(e, update)

            count = 0
            for entry in data:
                count += 1

                name = entry["name"]
                symbol = entry["symbol"].upper()
                vol = utl.format(entry["total_volume"])

                msg += f"#{count} {name} ({symbol})\n" \
                       f"{vol} {vs_cur.upper()}\n\n"

            msg = f"Top {top} by Total Volume\n\n{msg}"

        # ---------- TOTAL VOLUME ----------

        else:
            data = None

            try:
                response = APICache.get_cg_coins_list()
            except Exception as e:
                return self.handle_error(e, update)

            # Get coin ID and data
            for entry in response:
                if entry["symbol"] == coin:
                    try:
                        data = CoinGecko().get_coins_markets(
                            vs_cur,
                            ids=entry["id"],
                            order="volume_desc")
                    except Exception as e:
                        return self.handle_error(e, update)
                    break

            if not data:
                update.message.reply_text(
                    text=f"{emo.ERROR} No data for *{coin}*",
                    parse_mode=ParseMode.MARKDOWN)
                return

            name = data[0]["name"]
            vol = utl.format(data[0]["total_volume"])

            msg = f"{name} ({coin.upper()})\n\n" \
                  f"Total Volume:\n" \
                  f"{vol} {vs_cur.upper()}"

        if not msg:
            msg = f"{emo.ERROR} Can't retrieve data for *{coin.upper()}*"

        update.message.reply_text(
            text=f"`{msg}`",
            parse_mode=ParseMode.MARKDOWN)

    def get_usage(self):
        return f"`/{self.get_cmds()[0]} <symbol>(-<target symbol>) | top=<# of currencies>`"

    def get_description(self):
        return "Volume of a coin"

    def get_category(self):
        return Category.GENERAL
