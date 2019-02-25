import opencryptobot.emoji as emo
import opencryptobot.api.webscraping as webs

from telegram import ParseMode
from telegram.error import BadRequest
from opencryptobot.ratelimit import RateLimit
from opencryptobot.api.apicache import APICache
from opencryptobot.api.cryptocompare import CryptoCompare
from opencryptobot.plugin import OpenCryptoPlugin, Category


class Whitepaper(OpenCryptoPlugin):

    name = None

    def get_cmds(self):
        return ["wp", "whitepaper"]

    @OpenCryptoPlugin.save_data
    @OpenCryptoPlugin.send_typing
    def get_action(self, bot, update, args):
        if not args:
            update.message.reply_text(
                text=f"Usage:\n{self.get_usage()}",
                parse_mode=ParseMode.MARKDOWN)
            return

        coin = args[0].upper()

        search = str()
        if len(args) > 1:
            search = args[1]

        try:
            link = self._from_allcryptowhitepaper(coin)

            if not link:
                if RateLimit.limit_reached(update):
                    return

                link = self._from_coinmarketcap(coin)

            if not link and search == "all":
                link = self._from_coinpaprika(coin)
        except Exception as e:
            return self.handle_error(e, update)

        if link:
            try:
                update.message.reply_document(
                    document=link,
                    caption=f"{self.name} Whitepaper")
            except BadRequest:
                msg = f"{self.name} Whitepaper\n{link}"
                update.message.reply_text(text=msg)
        else:
            update.message.reply_text(
                text=f"{emo.INFO} No whitepaper for *{coin}* found",
                parse_mode=ParseMode.MARKDOWN)

    def get_usage(self):
        return f"`/{self.get_cmds()[0]} <symbol> (all)`"

    def get_description(self):
        return "Find whitepaper for a coin"

    def get_category(self):
        return Category.GENERAL

    def _from_allcryptowhitepaper(self, coin):
        coin_info = CryptoCompare().get_coin_general_info(coin, "USD")

        if coin_info["Message"] != "Success":
            return None

        self.name = coin_info["Data"][0]["CoinInfo"]["FullName"].replace(" ", "-")
        return webs.get_wp_allcryptowhitepaper(self.name)

    def _from_coinmarketcap(self, coin):
        slug = str()

        for listing in APICache.get_cmc_coin_list():
            if coin.upper() == listing["symbol"].upper():
                self.name = listing["name"].capitalize()
                slug = listing["website_slug"]
                break

        if not slug:
            return None

        return webs.get_wp_coinmarketcap(slug)

    def _from_coinpaprika(self, coin):
        coin_id = str()

        for c in APICache.get_cp_coin_list():
            if c["symbol"] == coin:
                self.name = c["name"]
                coin_id = c["id"]

        if not coin_id:
            return None

        return webs.get_wp_coinpaprika(coin_id)
