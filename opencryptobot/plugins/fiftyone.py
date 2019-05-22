import opencryptobot.emoji as emo

from telegram import ParseMode
from opencryptobot.ratelimit import RateLimit
from opencryptobot.api.crypto51 import Crypto51
from opencryptobot.plugin import OpenCryptoPlugin, Category


class Fiftyone(OpenCryptoPlugin):

    def get_cmds(self):
        return ["51", "fiftyone"]

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

        coin = args[0].upper()
        data = None

        try:
            coin_data = Crypto51().coins()
        except Exception as e:
            return self.handle_error(e, update)

        if not coin_data or not coin_data["coins"]:
            update.message.reply_text(
                text=f"{emo.INFO} No data for *{coin}*",
                parse_mode=ParseMode.MARKDOWN)
            return

        # Get coin ID and data
        for entry in coin_data["coins"]:
            if entry["symbol"] == coin:
                data = entry
                break

        if not data:
            update.message.reply_text(
                text=f"{emo.INFO} No data for *{coin}*",
                parse_mode=ParseMode.MARKDOWN)
            return

        name = data["name"]
        algo = data["algorithm"]
        mcap = data["market_cap_pretty"]
        hash = data["hash_rate_pretty"]
        atck = data["attack_hourly_cost_pretty"]
        hour = data["rentable_price_usd_hour"]

        update.message.reply_text(
            text=f"`PoW 51% Attack Cost\n`"
                 f"`for {coin} ({name})\n\n`"
                 f"`Algorithm      {algo}\n`"
                 f"`Market Cap     {mcap}\n`"
                 f"`Hashrate       {hash}\n`"
                 f"`Attack Cost 1h {atck}\n`"
                 f"`Rent. Price 1h {hour}`",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True)

    def get_usage(self):
        return f"`/{self.get_cmds()[0]} <symbol>`"

    def get_description(self):
        return "PoW 51% attack cost"

    def get_category(self):
        return Category.PRICE
