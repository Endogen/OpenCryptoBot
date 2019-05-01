import os
import json
import twitter
import logging
import opencryptobot.emoji as emo
import opencryptobot.constants as con

from telegram import ParseMode
from opencryptobot.ratelimit import RateLimit
from opencryptobot.api.apicache import APICache
from opencryptobot.api.coingecko import CoinGecko
from opencryptobot.plugin import OpenCryptoPlugin, Category


class Twitter(OpenCryptoPlugin):

    _consumer_key = None
    _consumer_secret = None
    _access_token_key = None
    _access_token_secret = None

    def __init__(self, telegram_bot):
        super().__init__(telegram_bot)

        token_path = os.path.join(con.CFG_DIR, con.TKN_FILE)
        
        try:
            if os.path.isfile(token_path):
                with open(token_path, 'r') as file:
                    tokens = json.load(file)

                    self._consumer_key = tokens["tw-consumer_key"]
                    self._consumer_secret = tokens["tw-consumer_secret"]
                    self._access_token_key = tokens["tw-access_token_key"]
                    self._access_token_secret = tokens["tw-access_token_secret"]
            else:
                logging.error(f"No token file '{con.TKN_FILE}' found at '{token_path}'")
        except KeyError as e:
            cls_name = f"Class: {type(self).__name__}"
            logging.error(f"{repr(e)} - {cls_name}")

    def get_cmds(self):
        return ["tw", "twitter"]

    @OpenCryptoPlugin.save_data
    @OpenCryptoPlugin.send_typing
    def get_action(self, bot, update, args):
        if not args:
            update.message.reply_text(
                text=f"Usage:\n{self.get_usage()}",
                parse_mode=ParseMode.MARKDOWN)
            return

        if RateLimit.limit_reached(update):
            return

        # Set tokens for Twitter access
        tw = twitter.Api(
            consumer_key=self._consumer_key,
            consumer_secret=self._consumer_secret,
            access_token_key=self._access_token_key,
            access_token_secret=self._access_token_secret)

        coin = args[0].upper()

        # Get coin ID
        try:
            response = APICache.get_cg_coins_list()
        except Exception as e:
            return self.handle_error(e, update)

        timeline = None
        for entry in response:
            if entry["symbol"].lower() == coin.lower():
                try:
                    data = CoinGecko().get_coin_by_id(entry["id"])
                except Exception as e:
                    return self.handle_error(e, update)

                coin_name = data["name"]
                tw_account = data["links"]["twitter_screen_name"]

                if tw_account:
                    timeline = tw.GetUserTimeline(
                        screen_name=tw_account,
                        count=3,
                        include_rts=False,
                        trim_user=True,
                        exclude_replies=True)
                break

        if timeline:
            for tweet in [i.AsDict() for i in reversed(timeline)]:
                stats = f"{emo.HEART} {tweet['favorite_count']} " \
                        f"{emo.REPEAT} {tweet['retweet_count']}"

                msg = f"*Tweet from {coin_name}*\n" \
                      f"{tweet['created_at'].split('+')[0]}\n" \
                      f"{stats}\n\n" \
                      f"{tweet['text']}"

                update.message.reply_text(text=msg, parse_mode=ParseMode.MARKDOWN)

    def get_usage(self):
        return f"`/{self.get_cmds()[0]} <symbol>`"

    def get_description(self):
        return "Get newest tweets for coin"

    def get_category(self):
        return Category.NEWS
