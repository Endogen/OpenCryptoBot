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
            if update.message:
                update.message.reply_text(
                    text=f"Usage:\n{self.get_usage(bot.name)}",
                    parse_mode=ParseMode.MARKDOWN)
            return

        if "-" in args[0]:
            pair = args[0].split("-", 1)
            vs_cur = pair[0].upper()
            coin = pair[1].upper()
        else:
            coin = args[0].upper()

        cg = CoinGecko()

        # Get coin ID and name
        coin_id = str()
        coin_name = str()
        for entry in cg.get_coins_list():
            if entry["symbol"].upper() == coin:
                coin_name = entry["name"]
                coin_id = entry["id"]
                break

        result = cg.get_simple_price(coin_id, vs_cur)

        if not result:
            msg = f"{emo.ERROR} Can't retrieve data for *{coin}*"
        else:
            msg = str(f"`{coin_name} ({coin})`\n")
            for _, prices in result.items():
                for key, value in prices.items():
                    value = "{0:.8f}".format(value)
                    msg += f"`{key.upper()}: {value}`\n"

        if update.message:
            update.message.reply_text(
                text=msg,
                parse_mode=ParseMode.MARKDOWN)
        else:
            return msg

    def get_usage(self, bot_name):
        return f"`" \
               f"/{self.get_cmd()} <coin>\n" \
               f"/{self.get_cmd()} <vs coin>-<coin>\n" \
               f"{bot_name} /{self.get_cmd()} <coin>.\n" \
               f"{bot_name} /{self.get_cmd()} <vs coin>-<coin>." \
               f"`"

    def get_description(self):
        return "Coin price"

    def inline_mode(self):
        return True
