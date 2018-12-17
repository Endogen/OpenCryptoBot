import opencryptobot.emoji as emo

from telegram import ParseMode
from opencryptobot.api.coingecko import CoinGecko
from opencryptobot.plugin import OpenCryptoPlugin, Category


class Search(OpenCryptoPlugin):

    def get_cmd(self):
        return "se"

    @OpenCryptoPlugin.send_typing
    @OpenCryptoPlugin.save_data
    def get_action(self, bot, update, args):
        if not args:
            update.message.reply_text(
                text=f"Usage:\n{self.get_usage()}",
                parse_mode=ParseMode.MARKDOWN)
            return

        search = args[0]
        msg = str()

        for entry in CoinGecko().get_coins_list(use_cache=True):
            if search.lower() in entry["name"].lower():
                name = entry["name"]
                symbol = entry["symbol"]

                msg += f"`{name} - {symbol.upper()}`\n"

        if msg:
            msg = f"`Coin-search for '{search}'`\n\n" + msg
        else:
            msg = f"{emo.ERROR} No coin with '*{search}*' found"

        update.message.reply_text(
            text=msg,
            parse_mode=ParseMode.MARKDOWN)

    def get_usage(self):
        return f"`/{self.get_cmd()} <coin name>`"

    def get_description(self):
        return "Search for symbol by coin name"

    def get_category(self):
        return Category.GENERAL
