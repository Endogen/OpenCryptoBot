import io
import time
import threading
import pandas as pd
import dateutil.parser
import plotly.io as pio
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
        time_frame = 72  # Hours
        resolution = None
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
            if args[1].isnumeric():
                time_frame = args[1]
            elif args[1].lower().endswith("m") and args[1][:-1].isnumeric():
                resolution = "MINUTE"
                time_frame = args[1][:-1]
            elif args[1].lower().endswith("h") and args[1][:-1].isnumeric():
                resolution = "HOUR"
                time_frame = args[1][:-1]
            elif args[1].lower().endswith("d") and args[1][:-1].isnumeric():
                resolution = "DAY"
                time_frame = args[1][:-1]

        from_cp = False

        if resolution == "MINUTE":
            ohlcv = CryptoCompare().get_historical_ohlcv_minute(coin, base_coin, time_frame)["Data"]
        elif resolution == "HOUR":
            ohlcv = CryptoCompare().get_historical_ohlcv_hourly(coin, base_coin, time_frame)["Data"]
        elif resolution == "DAY":
            ohlcv = CryptoCompare().get_historical_ohlcv_daily(coin, base_coin, time_frame)["Data"]
        else:
            ohlcv = CryptoCompare().get_historical_ohlcv_hourly(coin, base_coin, time_frame)["Data"]

        # TODO: Add this to cache
        # TODO: Check for valid base_coin
        if not ohlcv:
            for c in CoinPaprika().get_list_coins():
                if c["symbol"] == coin:
                    t_now = time.time()
                    time_frame = float(time_frame)

                    if resolution == "MINUTE":
                        t_dif = time_frame * 60
                        t_start = t_now - t_dif
                    elif resolution == "HOUR":
                        t_dif = time_frame * 60 * 60
                        t_start = t_now - t_dif
                    elif resolution == "DAY":
                        t_dif = time_frame * 60 * 60 * 24
                        t_start = t_now - t_dif
                    else:
                        t_dif = time_frame * 60 * 60
                        t_start = t_now - t_dif

                    # TODO: Data looks weird... Verify
                    ohlcv = CoinPaprika().get_historical_ohlc(c["id"], int(t_start), end=int(t_now))
                    from_cp = True

        if not ohlcv:
            update.message.reply_text(
                text=f"{emo.ERROR} No OHLC data for *{coin}*",
                parse_mode=ParseMode.MARKDOWN)
            return

        o = [value["open"] for value in ohlcv]
        h = [value["high"] for value in ohlcv]
        l = [value["low"] for value in ohlcv]
        c = [value["close"] for value in ohlcv]

        if from_cp:
            # TODO: Better import possible? Shorter possible?
            t = [time.mktime(dateutil.parser.parse(value["time_close"]).timetuple()) for value in ohlcv]
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
            photo=io.BufferedReader(BytesIO(pio.to_image(fig, format='webp'))),
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
