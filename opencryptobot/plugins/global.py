import io
import plotly.io as pio
import plotly.graph_objs as go
import opencryptobot.emoji as emo
import opencryptobot.utils as utl

from io import BytesIO
from telegram import ParseMode
from opencryptobot.ratelimit import RateLimit
from opencryptobot.api.coingecko import CoinGecko
from opencryptobot.plugin import OpenCryptoPlugin, Category


class Global(OpenCryptoPlugin):

    def get_cmds(self):
        return ["g", "global"]

    @OpenCryptoPlugin.save_data
    @OpenCryptoPlugin.send_typing
    def get_action(self, bot, update, args):
        if not args:
            update.message.reply_text(
                text=f"Usage:\n{self.get_usage()}",
                parse_mode=ParseMode.MARKDOWN)
            return

        sub_cmd = args[0]

        if not sub_cmd:
            update.message.reply_text(
                text=f"Usage:\n{self.get_usage()}",
                parse_mode=ParseMode.MARKDOWN)
            return

        if RateLimit.limit_reached(update):
            return

        msg = str()

        try:
            res = CoinGecko().get_global()
        except Exception as e:
            return self.handle_error(e, update)

        # ---------- Total Market Capital ----------

        if sub_cmd.lower() == "mcap":
            m_cap_usd = utl.format(res["total_market_cap"]["usd"])
            m_cap_eur = utl.format(res["total_market_cap"]["eur"])

            msg = f"`Total Market Capital`\n" \
                  f"`USD: {m_cap_usd}`\n" \
                  f"`EUR: {m_cap_eur}`"

        # ---------- Total Volume ----------

        elif sub_cmd.lower() == "vol":
            vol_usd = utl.format(res["total_volume"]["usd"])
            vol_eur = utl.format(res["total_volume"]["eur"])

            msg = f"`Total Volume (24h)`\n" \
                  f"`USD: {vol_usd}`\n" \
                  f"`EUR: {vol_eur}`"

        # ---------- Dominance ----------

        elif sub_cmd.lower() == "dom":
            m_cap_per = res["market_cap_percentage"]

            labels = list()
            values = list()

            msg = "`Dominance (Market Capital)`\n"
            for key in sorted(m_cap_per, key=m_cap_per.get, reverse=True):
                labels.append(key.upper())
                values.append(m_cap_per[key])

                value = utl.format(m_cap_per[key], decimals=2, force_length=True)
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

            try:
                trace = go.Pie(labels=labels, values=values)
                fig = go.Figure(data=[trace], layout=layout)
            except Exception as e:
                return self.handle_error(e, update)

            update.message.reply_photo(
                photo=io.BufferedReader(BytesIO(pio.to_image(fig, format="jpeg"))),
                caption=msg,
                parse_mode=ParseMode.MARKDOWN)

            return

        if not msg:
            msg = f"{emo.ERROR} Can't retrieve global data*"

        update.message.reply_text(
            text=msg,
            parse_mode=ParseMode.MARKDOWN)

    def get_usage(self):
        return f"`/{self.get_cmds()[0]} mcap | vol | dom\n`"

    def get_description(self):
        return "Global crypto data"

    def get_category(self):
        return Category.GENERAL
