import threading

from coinmarketcap import Market
from telegram import ParseMode
from telegram.ext import CommandHandler
from opencryptobot.plugin import OpenCryptoPlugin


class Stats(OpenCryptoPlugin):

    coin_id = ""
    data_btc = ""
    data_eur = ""

    def get_handler(self):
        return CommandHandler("stats", self._stats)

    @OpenCryptoPlugin.add_user
    @OpenCryptoPlugin.send_typing
    def _stats(self, bot, update, data):
        coin = data.pair.split("-")[1]
        listings = Market().listings()

        for listing in listings["data"]:
            if coin.upper() == listing["symbol"].upper():
                self.coin_id = listing["id"]
                break

        thread_usd = threading.Thread(target=self.market_btc())
        thread_eur = threading.Thread(target=self.market_eur())

        thread_usd.start()
        thread_eur.start()

        thread_usd.join()
        thread_eur.join()

        btc = self.data_btc["data"]
        symbol = btc["symbol"]
        slug = btc["website_slug"]
        rank = str(btc["rank"])
        sup_c = "{0:,}".format(int(btc["circulating_supply"]))
        sup_t = "{0:,}".format(int(btc["total_supply"]))

        usd = btc["quotes"]["USD"]
        p_usd = "{0:.8f}".format(usd["price"])
        v_24h = "{0:,}".format(int(usd["volume_24h"]))
        m_cap = "{0:,}".format(int(usd["market_cap"]))
        c_1h = str(usd["percent_change_1h"])
        c_24h = str(usd["percent_change_24h"])
        c_7d = str(usd["percent_change_7d"])

        btc = btc["quotes"]["BTC"]
        p_btc = "{0:.8f}".format(float(btc["price"]))

        eur = self.data_eur["data"]["quotes"]["EUR"]
        p_eur = "{0:.8f}".format(float(eur["price"]))

        update.message.reply_text(
            text=f"`{symbol}\n\n"
                 f"{p_usd} USD\n"
                 f"{p_eur} EUR\n"
                 f"{p_btc} BTC\n\n"
                 f"1h  {c_1h}%\n"
                 f"24h {c_24h}%\n"
                 f"7d  {c_7d}%\n\n"
                 f"CMC Rank: {rank}\n"
                 f"Volume 24h: {v_24h} USD\n"
                 f"Market Cap: {m_cap} USD\n"
                 f"Circ. Supp: {sup_c} {symbol}\n"
                 f"Total Supp: {sup_t} {symbol}`\n\n"
                 f"[Stats on CoinMarketCap](https://coinmarketcap.com/currencies/{slug})\n"
                 f"[Stats on Coinlib](https://coinlib.io/coin/{coin}/{coin})",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True)

    def market_btc(self):
        self.data_btc = Market().ticker(self.coin_id, convert="BTC")

    def market_eur(self):
        self.data_eur = Market().ticker(self.coin_id, convert="EUR")
