import opencryptobot.emoji as emo

from telegram import ParseMode
from opencryptobot.api.apicache import APICache
from opencryptobot.api.coinpaprika import CoinPaprika
from opencryptobot.plugin import OpenCryptoPlugin, Category


class People(OpenCryptoPlugin):

    def get_cmd(self):
        return "pe"

    @OpenCryptoPlugin.send_typing
    @OpenCryptoPlugin.save_data
    def get_action(self, bot, update, args):
        if not args:
            update.message.reply_text(
                text=f"Usage:\n{self.get_usage()}",
                parse_mode=ParseMode.MARKDOWN)
            return

        coin = args[0].upper()
        msg = str()

        for c in APICache.get_cp_coin_list():
            if c["symbol"] == coin:
                for person in CoinPaprika().get_coin_by_id(c["id"])["team"]:
                    msg += f"{person['name']}\n{person['position']}\n\n"
                break

        if not msg:
            update.message.reply_text(
                text=f"{emo.ERROR} No team data for *{coin}*",
                parse_mode=ParseMode.MARKDOWN)
            return

        msg = f"`Team behind {coin}\n\n{msg}`"

        update.message.reply_text(
            text=msg,
            parse_mode=ParseMode.MARKDOWN)

    def get_usage(self):
        return f"`/{self.get_cmd()} <coin>`"

    def get_description(self):
        return "Info about team behind a coin"

    def get_category(self):
        return Category.GENERAL
