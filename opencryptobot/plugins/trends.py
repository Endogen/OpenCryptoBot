import io
import plotly.io as pio
import plotly.graph_objs as go
import opencryptobot.emoji as emo

from io import BytesIO
from telegram import ParseMode
from pytrends.request import TrendReq
from opencryptobot.plugin import OpenCryptoPlugin, Category


class Trends(OpenCryptoPlugin):

    def get_cmd(self):
        return "tr"

    @OpenCryptoPlugin.send_typing
    @OpenCryptoPlugin.save_data
    def get_action(self, bot, update, args):
        if not args:
            update.message.reply_text(
                text=f"Usage:\n{self.get_usage()}",
                parse_mode=ParseMode.MARKDOWN)
            return

        pytrends = TrendReq(hl='en-US', tz=360)
        pytrends.build_payload(args, cat=0, timeframe='today 5-y', geo='', gprop='')

        data = pytrends.interest_over_time()

        tr_data = list()
        for kw in args:
            tr_data.append(go.Scatter(x=data.get("date"), y=data.get(kw)))

        fig = go.Figure(data=tr_data)

        update.message.reply_photo(
            photo=io.BufferedReader(BytesIO(pio.to_image(fig, format="jpeg"))),
            parse_mode=ParseMode.MARKDOWN)

    def get_usage(self):
        return f"`/{self.get_cmd()} <keyword> (<keyword> ...)`"

    def get_description(self):
        return "Google Trends - Interest Over Time"

    def get_category(self):
        return Category.GENERAL
