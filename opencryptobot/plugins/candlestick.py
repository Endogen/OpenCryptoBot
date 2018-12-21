import io
import time
import threading
import pandas as pd
import plotly.io as pio
import dateutil.parser as dau
import plotly.graph_objs as go
import opencryptobot.emoji as emo
import plotly.figure_factory as fif
import opencryptobot.constants as con

from io import BytesIO
from telegram import ParseMode
from coinmarketcap import Market
from opencryptobot.api.coinpaprika import CoinPaprika
from opencryptobot.api.cryptocompare import CryptoCompare
from opencryptobot.plugin import OpenCryptoPlugin, Category


class Candlestick(OpenCryptoPlugin):

    cmc_coin_id = None

    def get_cmd(self):
        return "cs"

    @OpenCryptoPlugin.send_typing
    @OpenCryptoPlugin.save_data
    def get_action(self, bot, update, args):
        time_frame = 72
        resolution = "HOUR"
        base_coin = "BTC"

        if not args:
            update.message.reply_text(
                text=f"Usage:\n{self.get_usage()}",
                parse_mode=ParseMode.MARKDOWN)
            return

        # TODO: Doesn't work. Why?
        # Coin or pair
        if "-" in args[0]:
            pair = args[0].split("-", 1)
            base_coin = pair[0].upper()
            coin = pair[1].upper()
        else:
            coin = args[0].upper()

        if coin == "BTC" and base_coin == "BTC":
            base_coin = "USD"

        if coin == base_coin:
            update.message.reply_text(
                text=f"{emo.ERROR} Can't compare *{coin}* to itself",
                parse_mode=ParseMode.MARKDOWN)
            return

        cmc_thread = threading.Thread(target=self._get_cmc_coin_id, args=[coin])
        cmc_thread.start()

        # Time frame
        if len(args) > 1:
            if args[1].lower().endswith("m") and args[1][:-1].isnumeric():
                resolution = "MINUTE"
                time_frame = args[1][:-1]
            elif args[1].lower().endswith("h") and args[1][:-1].isnumeric():
                resolution = "HOUR"
                time_frame = args[1][:-1]
            elif args[1].lower().endswith("d") and args[1][:-1].isnumeric():
                resolution = "DAY"
                time_frame = args[1][:-1]
            else:
                update.message.reply_text(
                    text=f"{emo.ERROR} Argument *{args[1]}* is invalid",
                    parse_mode=ParseMode.MARKDOWN)
                return

        if resolution == "MINUTE":
            ohlcv = CryptoCompare().get_historical_ohlcv_minute(
                coin,
                base_coin,
                time_frame)
        elif resolution == "HOUR":
            ohlcv = CryptoCompare().get_historical_ohlcv_hourly(
                coin,
                base_coin,
                time_frame)
        elif resolution == "DAY":
            ohlcv = CryptoCompare().get_historical_ohlcv_daily(
                coin,
                base_coin,
                time_frame)

        if ohlcv["Response"] == "Error":
            if ohlcv["Message"] == "limit is larger than max value.":
                update.message.reply_text(
                    text=f"{emo.ERROR} Time frame can't be larger "
                    f"then *{con.CG_DATA_LIMIT}* data points",
                    parse_mode=ParseMode.MARKDOWN)
                return
            elif ohlcv["Message"].startswith("There is no data for the symbol"):
                ohlcv = None
            else:
                update.message.reply_text(
                    text=f"{emo.ERROR} CoinGecko ERROR: {ohlcv['Message']}",
                    parse_mode=ParseMode.MARKDOWN)
                return
        else:
            ohlcv = ohlcv["Data"]

        cp_api = False
        # TODO: Add this to cache
        if not ohlcv:
            if base_coin != "BTC" and base_coin != "USD":
                update.message.reply_text(
                    text=f"{emo.ERROR} Base currency for "
                    f"*{coin}* can only be *BTC* or *USD*",
                    parse_mode=ParseMode.MARKDOWN)
                return

            # Time frame
            if len(args) > 1:
                if resolution != "DAY":
                    update.message.reply_text(
                        text=f"{emo.ERROR} Timeframe for *{coin}* "
                        f"can only be specified in days",
                        parse_mode=ParseMode.MARKDOWN)
                    return
                else:
                    time_frame = int(time_frame)
            else:
                time_frame = 30  # Days

            for c in CoinPaprika().get_list_coins():
                if c["symbol"] == coin:
                    # Current datetime in seconds
                    t_now = time.time()
                    # Convert chart time span to seconds
                    time_frame = time_frame * 24 * 60 * 60
                    # Start datetime for chart in seconds
                    t_start = t_now - int(time_frame)

                    ohlcv = CoinPaprika().get_historical_ohlc(
                        c["id"],
                        int(t_start),
                        end=int(t_now),
                        quote=base_coin.lower(),
                        limit=366)

                    cp_api = True
                    break

            if not ohlcv:
                update.message.reply_text(
                    text=f"{emo.ERROR} No OHLC data for *{coin}* "
                    f"available or time frame too big",
                    parse_mode=ParseMode.MARKDOWN)
                return

        o = [value["open"] for value in ohlcv]
        h = [value["high"] for value in ohlcv]
        l = [value["low"] for value in ohlcv]
        c = [value["close"] for value in ohlcv]

        if cp_api:
            t = [time.mktime(dau.parse(value["time_close"]).timetuple()) for value in ohlcv]
        else:
            t = [value["time"] for value in ohlcv]

        margin_l = 140
        tickformat = "0.8f"

        max_value = max(h)
        if max_value > 0.9:
            if max_value > 999:
                margin_l = 120
                tickformat = "0,.0f"
            else:
                margin_l = 125
                tickformat = "0.2f"

        fig = fif.create_candlestick(o, h, l, c, pd.to_datetime(t, unit='s'))

        fig['layout']['yaxis'].update(
            tickformat=tickformat,
            tickprefix="   ",
            ticksuffix=f"  ")

        fig['layout'].update(
            title=coin,
            titlefont=dict(
                size=26
            ),
            yaxis=dict(
                title=base_coin,
                titlefont=dict(
                    size=18
                )
            )
        )

        fig['layout'].update(
            shapes=[{
                "type": "line",
                "xref": "paper",
                "yref": "y",
                "x0": 0,
                "x1": 1,
                "y0": c[len(c) - 1],
                "y1": c[len(c) - 1],
                "line": {
                    "color": "rgb(50, 171, 96)",
                    "width": 1,
                    "dash": "dot"
                }
            }])

        fig['layout'].update(
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
            ))

        cmc_thread.join()

        fig['layout'].update(
            images=[dict(
                source=f"{con.CMC_LOGO_URL_PARTIAL}{self.cmc_coin_id}.png",
                opacity=0.8,
                xref="paper", yref="paper",
                x=1.05, y=1,
                sizex=0.2, sizey=0.2,
                xanchor="right", yanchor="bottom"
            )])

        update.message.reply_photo(
            photo=io.BufferedReader(BytesIO(pio.to_image(fig, format='jpeg'))),
            parse_mode=ParseMode.MARKDOWN)

    def get_usage(self):
        return f"`" \
               f"/{self.get_cmd()} <coin> (<# of hours>)\n" \
               f"/{self.get_cmd()} <vs coin>-<coin> (<# of hours>)" \
               f"`"

    def get_description(self):
        return "Candlestick chart for coin"

    def get_category(self):
        return Category.CHARTS

    def _get_cmc_coin_id(self, ticker):
        for listing in Market().listings()["data"]:
            if ticker.upper() == listing["symbol"].upper():
                self.cmc_coin_id = listing["id"]
                break
