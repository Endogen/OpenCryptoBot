from telegram import ParseMode
import opencryptobot.emoji as emo
from opencryptobot.api.coingecko import CoinGecko
from opencryptobot.plugin import OpenCryptoPlugin


class Price(OpenCryptoPlugin):

    def get_cmd(self):
        return "p"

    @OpenCryptoPlugin.send_typing
    @OpenCryptoPlugin.save_data
    def get_action(self, bot, update, args):
        vs_cur = "BTC,ETH,EUR,USD"

        if not args:
            update.message.reply_text(
                text=f"Usage:\n{self.get_usage()}",
                parse_mode=ParseMode.MARKDOWN)
            return

        if "-" in args[0]:
            pair = args[0].split("-", 1)
            vs_cur = pair[0]
            coin = pair[1]
        else:
            coin = args[0]

        cg = CoinGecko()

        # Get coin ID
        coin_id = str()
        for entry in cg.get_coins_list():
            if entry["symbol"].lower() == coin.lower():
                coin_id = entry["id"]
                break

        result = cg.get_simple_price(coin_id, vs_cur)

        msg = str()
        for _, prices in result.items():
            for key, value in prices.items():
                value = self.trm_zro(value)
                msg += f"`{key.upper()}: {value}`\n"

        if not msg:
            msg = f"{emo.ERROR} Trading pair *{args[0].upper()}* not supported"

        update.message.reply_text(
            text=msg,
            parse_mode=ParseMode.MARKDOWN)

    def get_usage(self):
        return f"`/{self.get_cmd()} <coin> | <base coin>-<coin>`"

    def get_description(self):
        return "Price for coin"
