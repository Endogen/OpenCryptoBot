import io
import plotly.io as pio
import plotly.graph_objs as go
import opencryptobot.emoji as emo

from io import BytesIO
from telegram import ParseMode
from opencryptobot.utils import format
from opencryptobot.ratelimit import RateLimit
from opencryptobot.api.coingecko import CoinGecko
from opencryptobot.plugin import OpenCryptoPlugin, Category


class Global(OpenCryptoPlugin):

    def get_cmd(self):
        return "g"

    @OpenCryptoPlugin.save_data
    @OpenCryptoPlugin.send_typing
    def get_action(self, bot, update, args):
        if not args:
            update.message.reply_text(
                text=f"Usage:\n{self.get_usage()}",
                parse_mode=ParseMode.MARKDOWN)
            return

        sub_cmd = args[0]

        coin = str()
        if len(args) > 1:
            coin = args[1]

        if not sub_cmd:
            update.message.reply_text(
                text=f"Usage:\n{self.get_usage()}",
                parse_mode=ParseMode.MARKDOWN)
            return

        if RateLimit.limit_reached(update):
            return

        msg = str()
        res = CoinGecko().get_global()

        # Total Market Capital
        if sub_cmd.lower() == "mcap":
            m_cap_usd = format(res["total_market_cap"]["usd"])
            m_cap_eur = format(res["total_market_cap"]["eur"])

            if coin:
                if coin in res["total_market_cap"]:
                    mcap = format(res["total_market_cap"][coin])
                    msg = f"`Total Market Capital\n{coin.upper()}: {mcap}`"
            else:
                msg = f"`Total Market Capital`\n" \
                      f"`USD: {m_cap_usd}`\n" \
                      f"`EUR: {m_cap_eur}`"

        # Total Volume
        elif sub_cmd.lower() == "vol":
            vol_usd = format(res["total_volume"]["usd"])
            vol_eur = format(res["total_volume"]["eur"])

            if coin:
                if coin in res["total_volume"]:
                    vol = format(res["total_volume"][coin])
                    msg = f"`Total Volume\n{coin.upper()}: {vol}`"
            else:
                msg = f"`Total Volume (24h)`\n" \
                      f"`USD: {vol_usd}`\n" \
                      f"`EUR: {vol_eur}`"

        elif sub_cmd.lower() == "dom":
            m_cap_per = res["market_cap_percentage"]

            labels = list()
            values = list()

            msg = "`Dominance (Market Capital)`\n"
            for key in sorted(m_cap_per, key=m_cap_per.get, reverse=True):
                labels.append(key.upper())
                values.append(m_cap_per[key])

                value = format(m_cap_per[key], decimals=2, force_length=True)
                tst = "{:>13}".format(f"{value}%")
                tst = key.upper() + tst[len(key):]
                msg += f"`{tst}`\n"

            labels.append("[Other]")
            values.append(100 - sum(values))

            layout = go.Layout(
                paper_bgcolor='rgb(233,233,233)',
                plot_bgcolor='rgb(233,233,233)',
                autosize=True,
                margin=go.layout.Margin(
                    l=20,
                    r=20,
                    b=20,
                    t=20,
                    pad=4
                )
            )

            trace = go.Pie(labels=labels, values=values)
            fig = go.Figure(data=[trace], layout=layout)

            update.message.reply_photo(
                photo=io.BufferedReader(BytesIO(pio.to_image(fig, format="jpeg"))),
                caption=msg,
                parse_mode=ParseMode.MARKDOWN)

            return

        if not msg:
            msg = f"{emo.ERROR} Can't retrieve data for *{coin.upper()}*"

        update.message.reply_text(
            text=msg,
            parse_mode=ParseMode.MARKDOWN)

    def get_usage(self):
        return f"`" \
               f"/{self.get_cmd()} mcap (<coin>)\n" \
               f"/{self.get_cmd()} vol (<coin>)\n" \
               f"/{self.get_cmd()} dom" \
               f"`"

    def get_description(self):
        return "Global crypto data"

    def get_category(self):
        return Category.GENERAL
