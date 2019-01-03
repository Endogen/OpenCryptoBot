import os
import logging
import opencryptobot.emoji as emo
import opencryptobot.constants as con

from datetime import datetime
from telegram import ParseMode
from opencryptobot.api.apicache import APICache
from opencryptobot.api.cryptopanic import CryptoPanic
from opencryptobot.plugin import OpenCryptoPlugin, Category


class News(OpenCryptoPlugin):

    _token = None

    def __init__(self, updater, db):
        super().__init__(updater, db)

        token_path = os.path.join(con.CFG_DIR, con.CRYPAN_TKN_FILE)

        if os.path.isfile(token_path):
            with open(token_path, 'r') as file:
                self._token = file.read()
        else:
            logging.error(f"No token file found at '{token_path}'")

    def get_cmd(self):
        return "news"

    @OpenCryptoPlugin.send_typing
    @OpenCryptoPlugin.save_data
    def get_action(self, bot, update, args):
        if not args:
            update.message.reply_text(
                text=f"Usage:\n{self.get_usage()}",
                parse_mode=ParseMode.MARKDOWN)
            return

        symbol = args[0].upper()

        filter = None
        if len(args) > 1:
            if args[1].lower().startswith("filter="):
                filter = args[1][7:]

        if filter:
            data = CryptoPanic(token=self._token).get_multiple_filters(symbol, filter)
            msg = str(f"News for <b>{symbol}</b> and filter '{filter}'\n\n")
        else:
            data = CryptoPanic(token=self._token).get_currency_news(symbol)
            msg = str(f"News for <b>{symbol}</b>\n\n")

        if not data or not data["results"]:
            update.message.reply_text(
                text=f"{emo.ERROR} Couldn't get news for *{symbol}*",
                parse_mode=ParseMode.MARKDOWN)
            return

        for news in data["results"]:
            if news["kind"] == "news":
                published = news["published_at"]
                domain = news["domain"]
                title = news["title"]
                url = news["url"]

                t = datetime.fromisoformat(published.replace("Z", "+00:00"))
                month = f"0{t.month}" if len(str(t.month)) == 1 else t.month
                day = f"0{t.day}" if len(str(t.day)) == 1 else t.day
                hour = f"0{t.hour}" if len(str(t.hour)) == 1 else t.hour
                minute = f"0{t.minute}" if len(str(t.minute)) == 1 else t.minute

                msg += f'{t.year}-{month}-{day} {hour}:{minute} - {domain}\n' \
                       f'<a href="{url}">{title.strip()}</a>\n\n'

        update.message.reply_text(
            text=msg,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True)

    def get_usage(self):
        return f"`/{self.get_cmd()} <coin> (filter=<filter>)`"

    def get_description(self):
        return "News about a coin"

    def get_category(self):
        return Category.NEWS
