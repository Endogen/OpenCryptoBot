import requests
import opencryptobot.emoji as emo
import opencryptobot.constants as con

from bs4 import BeautifulSoup
from telegram import ParseMode
from telegram.error import BadRequest
from opencryptobot.api.apicache import APICache
from opencryptobot.api.cryptocompare import CryptoCompare
from opencryptobot.plugin import OpenCryptoPlugin, Category


class Whitepaper(OpenCryptoPlugin):

    name = None

    def get_cmd(self):
        return "wp"

    @OpenCryptoPlugin.send_typing
    @OpenCryptoPlugin.save_data
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

        link = self._from_allcryptowhitepaper(coin)

        if not link:
            link = self._from_coinmarketcap(coin)
        if not link and search == "all":
            link = self._from_coinpaprika(coin)

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
                text=f"{emo.ERROR} No whitepaper for *{coin}* found",
                parse_mode=ParseMode.MARKDOWN)

    def get_usage(self):
        return f"`/{self.get_cmd()} <coin> ('all')`"

    def get_description(self):
        return "Find whitepaper for a coin"

    def get_category(self):
        return Category.GENERAL

    def _from_allcryptowhitepaper(self, coin):
        coin_info = CryptoCompare().get_coin_general_info(coin, "USD")

        if coin_info["Message"] != "Success":
            return None

        self.name = coin_info["Data"][0]["CoinInfo"]["FullName"].replace(" ", "-")
        url = f"{con.ALL_CRYPTO_WP_PARTIAL}{self.name}-Whitepaper"
        response = requests.get(url)

        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.content, "html.parser")
        for entry_content in soup.find_all(class_="entry-content"):
            for p in entry_content.find_all("p"):
                for a in p.find_all("a"):
                    if "".join(a.get_text().split()) == f"{self.name}Whitepaper":
                        return a["href"]

    def _from_coinmarketcap(self, coin):
        slug = str()

        for listing in APICache.get_cmc_coin_list():
            if coin.upper() == listing["symbol"].upper():
                self.name = listing["name"].capitalize()
                slug = listing["website_slug"]
                break

        if not slug:
            return None

        url = f"{con.CMC_URL_PARTIAL}{slug}"
        response = requests.get(url)

        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.content, "html.parser")
        for links in soup.find_all(class_="list-unstyled details-panel-item--links"):
            for li in links.find_all("li"):
                if li.find_all(class_="glyphicons glyphicons-file details-list-item-icon"):
                    for a in li.find_all("a"):
                        return a["href"]

    def _from_coinpaprika(self, coin):
        coin_id = str()

        for c in APICache.get_cp_coin_list():
            if c["symbol"] == coin:
                self.name = c["name"]
                coin_id = c["id"]

        if not coin_id:
            return None

        url = f"{con.COIN_PAPRIKA_PARTIAL}{coin_id}"
        response = requests.get(url)

        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.content, "html.parser")
        for link in soup.find_all(class_="cp-details__whitepaper-link"):
            return link["href"]
