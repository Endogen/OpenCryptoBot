from telegram import ParseMode
from opencryptobot.plugin import OpenCryptoPlugin
from opencryptobot.api.coingecko import CoinGecko


class Global(OpenCryptoPlugin):

    def get_cmd(self):
        return "g"

    @OpenCryptoPlugin.send_typing
    @OpenCryptoPlugin.save_data
    def get_action(self, bot, update, args):
        #if not args:
        #    update.message.reply_text(
        #        text=f"Usage:\n{self.get_usage()}",
        #        parse_mode=ParseMode.MARKDOWN)
        #    return

        response = CoinGecko().get_global()

        update.message.reply_text(
            text=str(response),
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True)

    def get_usage(self):
        return f"`/{self.get_cmd()} <coin>`"

    def get_description(self):
        return "Coin description"
