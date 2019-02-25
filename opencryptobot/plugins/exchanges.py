import opencryptobot.emoji as emo
import opencryptobot.utils as utl

from telegram import ParseMode
from opencryptobot.ratelimit import RateLimit
from opencryptobot.api.apicache import APICache
from opencryptobot.plugin import OpenCryptoPlugin, Category


class Exchanges(OpenCryptoPlugin):

    def get_cmds(self):
        return ["ex", "exchange"]

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
        exchange = str()

        if args[0].lower().startswith("top="):
            top = args[0][4:]
        else:
            exchange = args[0]

        # ---------- TOP EXCHANGES ----------

        if top:
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

            if RateLimit.limit_reached(update):
                return

            try:
                response = APICache.get_cg_exchanges_list()
            except Exception as e:
                return self.handle_error(e, update)

            exchanges = sorted(
                response,
                key=lambda k: float(k["trade_volume_24h_btc"]), reverse=True)

            for i in range(int(top)):
                ex = exchanges[i]

                nr = f"#{i+1}"
                name = ex["name"]
                volume = ex["trade_volume_24h_btc"]

                msg += f"`{nr} {name}\n{utl.format(volume)} BTC`\n\n"

            msg = f"`Top {top} exchanges by 24h volume`\n\n{msg}"

        # ---------- EXCHANGE DETAILS ----------

        else:
            if RateLimit.limit_reached(update):
                return

            try:
                response = APICache.get_cg_exchanges_list()
            except Exception as e:
                return self.handle_error(e, update)

            for ex in response:
                clean_ex = ex["name"].replace(" ", "")
                if exchange.lower() in clean_ex.lower():
                    nme = ex["name"] if ex["name"] else "N/A"
                    est = ex["year_established"] if ex["year_established"] else "N/A"
                    cnt = ex["country"] if ex["country"] else "N/A"
                    des = ex["description"] if ex["description"] else "(No description available)"
                    url = ex["url"] if ex["url"] else "(No link available)"
                    vol = ex["trade_volume_24h_btc"] if ex["trade_volume_24h_btc"] else "N/A"

                    msg += f"`{nme}`\n" \
                           f"{utl.url(url)}\n\n" \
                           f"`Country:     {cnt}`\n" \
                           f"`Volume 24h:  {utl.format(vol)} BTC`\n" \
                           f"`Established: {est}`\n\n" \
                           f"`{utl.remove_html_links(des)}`\n\n\n" \

        if not msg:
            update.message.reply_text(
                text=f"{emo.INFO} No exchange '{exchange}' found",
                parse_mode=ParseMode.MARKDOWN)
            return

        update.message.reply_text(
            text=msg,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True)

    def get_usage(self):
        return f"`/{self.get_cmds()[0]} <exchange> | top=<# of exchanges>`"

    def get_description(self):
        return "Exchange details and toplist"

    def get_category(self):
        return Category.GENERAL
