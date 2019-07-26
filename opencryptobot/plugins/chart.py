import io
import threading
import pandas as pd
import plotly.io as pio
import plotly.graph_objs as go
import opencryptobot.emoji as emo
import opencryptobot.utils as utl
import opencryptobot.constants as con

from io import BytesIO
from pandas import DataFrame
from telegram import ParseMode
from opencryptobot.ratelimit import RateLimit
from opencryptobot.api.apicache import APICache
from opencryptobot.api.coingecko import CoinGecko
from opencryptobot.plugin import OpenCryptoPlugin, Category, Keyword


class Chart(OpenCryptoPlugin):

    cg_coin_id = None
    cmc_coin_id = None

    def get_cmds(self):
        return ["c", "chart"]

    @OpenCryptoPlugin.save_data
    @OpenCryptoPlugin.send_typing
    def get_action(self, bot, update, args):
        keywords = utl.get_kw(args)
        arg_list = utl.del_kw(args)

        if not arg_list:
            if not keywords.get(Keyword.INLINE):
                update.message.reply_text(
                    text=f"Usage:\n{self.get_usage()}",
                    parse_mode=ParseMode.MARKDOWN)
            return

        time_frame = 3  # Days
        base_coin = "BTC"

        if "-" in arg_list[0]:
            pair = arg_list[0].split("-", 1)
            base_coin = pair[1].upper()
            coin = pair[0].upper()
        else:
            coin = arg_list[0].upper()

        if coin == "BTC" and base_coin == "BTC":
            base_coin = "USD"

        if coin == base_coin:
            update.message.reply_text(
                text=f"{emo.ERROR} Can't compare *{coin}* to itself",
                parse_mode=ParseMode.MARKDOWN)
            return

        if len(arg_list) > 1 and arg_list[1].isnumeric():
            time_frame = arg_list[1]

        if RateLimit.limit_reached(update):
            return

        cg_thread = threading.Thread(target=self._get_cg_coin_id, args=[coin])
        cmc_thread = threading.Thread(target=self._get_cmc_coin_id, args=[coin])

        cg_thread.start()
        cmc_thread.start()

        cg_thread.join()

        if not self.cg_coin_id:
            update.message.reply_text(
                text=f"{emo.ERROR} Can't retrieve data for *{coin}*",
                parse_mode=ParseMode.MARKDOWN)
            return

        try:
            market = CoinGecko().get_coin_market_chart_by_id(
                self.cg_coin_id,
                base_coin.lower(),
                time_frame)
        except Exception as e:
            return self.handle_error(e, update)

        # Volume
        df_volume = DataFrame(market["total_volumes"], columns=["DateTime", "Volume"])
        df_volume["DateTime"] = pd.to_datetime(df_volume["DateTime"], unit="ms")
        volume = go.Scatter(
            x=df_volume.get("DateTime"),
            y=df_volume.get("Volume"),
            name="Volume"
        )

        # Price
        df_price = DataFrame(market["prices"], columns=["DateTime", "Price"])
        df_price["DateTime"] = pd.to_datetime(df_price["DateTime"], unit="ms")
        price = go.Scatter(
            x=df_price.get("DateTime"),
            y=df_price.get("Price"),
            yaxis="y2",
            name="Price",
            line=dict(
                color=("rgb(22, 96, 167)"),
                width=2
            )
        )

        cmc_thread.join()

        if not self.cmc_coin_id:
            update.message.reply_text(
                text=f"{emo.ERROR} Can't retrieve data for *{coin}*",
                parse_mode=ParseMode.MARKDOWN)
            return

        margin_l = 140
        tickformat = "0.8f"

        max_value = df_price["Price"].max()
        if max_value > 0.9:
            if max_value > 999:
                margin_l = 110
                tickformat = "0,.0f"
            else:
                margin_l = 115
                tickformat = "0.2f"

        layout = go.Layout(
            images=[dict(
                source=f"{con.CMC_LOGO_URL_PARTIAL}{self.cmc_coin_id}.png",
                opacity=0.8,
                xref="paper", yref="paper",
                x=1.05, y=1,
                sizex=0.2, sizey=0.2,
                xanchor="right", yanchor="bottom"
            )],
            paper_bgcolor='rgb(233,233,233)',
            plot_bgcolor='rgb(233,233,233)',
            autosize=False,
            width=800,
            height=600,
            margin=go.layout.Margin(
                l=margin_l,
                r=50,
                b=85,
                t=100,
                pad=4
            ),
            yaxis=dict(
                domain=[0, 0.20]
            ),
            yaxis2=dict(
                title=dict(
                    text=base_coin,
                    font=dict(
                        size=18
                    )
                ),                domain=[0.25, 1],
                tickprefix="   ",
                ticksuffix=f"  "
            ),
            title=dict(
                text=coin,
                font=dict(
                    size=26
                )
            ),
            legend=dict(
                orientation="h",
                yanchor="top",
                xanchor="center",
                y=1.05,
                x=0.45
            ),
            shapes=[{
                "type": "line",
                "xref": "paper",
                "yref": "y2",
                "x0": 0,
                "x1": 1,
                "y0": market["prices"][len(market["prices"]) - 1][1],
                "y1": market["prices"][len(market["prices"]) - 1][1],
                "line": {
                    "color": "rgb(50, 171, 96)",
                    "width": 1,
                    "dash": "dot"
                }
            }],
        )

        try:
            fig = go.Figure(data=[price, volume], layout=layout)
        except Exception as e:
            return self.handle_error(e, update)

        fig["layout"]["yaxis2"].update(tickformat=tickformat)

        self.send_photo(
            io.BufferedReader(BytesIO(pio.to_image(fig, format='jpeg'))),
            update,
            keywords)

    def get_usage(self):
        return f"`/{self.get_cmds()[0]} <symbol>(-<target symbol>) (<# of days>)`"

    def get_description(self):
        return "Chart with price and volume"

    def get_category(self):
        return Category.CHARTS

    def _get_cg_coin_id(self, coin):
        try:
            for entry in APICache.get_cg_coins_list():
                if entry["symbol"].lower() == coin.lower():
                    self.cg_coin_id = entry["id"]
                    break
        except:
            self.cg_coin_id = None

    def _get_cmc_coin_id(self, coin):
        self.cmc_coin_id = None
        for listing in APICache.get_cmc_coin_list():
            if coin == listing["symbol"].upper():
                self.cmc_coin_id = listing["id"]
                break
