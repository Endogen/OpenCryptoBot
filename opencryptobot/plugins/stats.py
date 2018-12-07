import threading
import opencryptobot.emoji as emo

from coinmarketcap import Market
from telegram import ParseMode
from opencryptobot.plugin import OpenCryptoPlugin


class Stats(OpenCryptoPlugin):

    coin_id = None
    data_btc = None
    data_eur = None

    def get_cmd(self):
        return "s"

    @OpenCryptoPlugin.send_typing
    @OpenCryptoPlugin.save_data
    def get_action(self, bot, update, args):
        if not args:
            update.message.reply_text(
                text=f"Usage:\n{self.get_usage()}",
                parse_mode=ParseMode.MARKDOWN)
            return

        coin = args[0]

        self.coin_id = None
        listings = Market().listings()
        for listing in listings["data"]:
            if coin.upper() == listing["symbol"].upper():
                self.coin_id = listing["id"]
                break

        if not self.coin_id:
            update.message.reply_text(
                text=f"{emo.ERROR} Can't retrieve data for *{coin.upper()}*",
                parse_mode=ParseMode.MARKDOWN)
            return

        thread_usd = threading.Thread(target=self.market_btc())
        thread_eur = threading.Thread(target=self.market_eur())

        thread_usd.start()
        thread_eur.start()

        thread_usd.join()
        thread_eur.join()

        btc = self.data_btc["data"]
        name = btc["name"]
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
        c_1d = str(usd["percent_change_24h"])
        c_7d = str(usd["percent_change_7d"])

        btc = btc["quotes"]["BTC"]
        p_btc = "{0:.8f}".format(float(btc["price"]))

        eur = self.data_eur["data"]["quotes"]["EUR"]
        p_eur = "{0:.8f}".format(float(eur["price"]))

        c1h = "{0:.2f}".format(float(c_1h))
        c1d = "{0:.2f}".format(float(c_1d))
        c7d = "{0:.2f}".format(float(c_7d))

        h1 = "{:>11}".format(f"{c1h}%")
        d1 = "{:>11}".format(f"{c1d}%")
        d7 = "{:>11}".format(f"{c7d}%")

        update.message.reply_text(
            text=f"`"
                 f"{name} ({symbol})\n\n"
                 f"{p_usd} USD\n"
                 f"{p_eur} EUR\n"
                 f"{p_btc} BTC\n\n"
                 f"1h {h1}\n"
                 f"1d {d1}\n"
                 f"7d {d7}\n\n"
                 f"CMC Rank: {rank}\n"
                 f"Volume 24h: {v_24h} USD\n"
                 f"Market Cap: {m_cap} USD\n"
                 f"Circ. Supp: {sup_c} {symbol}\n"
                 f"Total Supp: {sup_t} {symbol}\n\n"
                 f"`"
                 f"Stats on [CoinMarketCap](https://coinmarketcap.com/currencies/{slug}) & "
                 f"[Coinlib](https://coinlib.io/coin/{coin}/{coin})",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True)

    def get_usage(self):
        return f"`/{self.get_cmd()} <coin>`"

    def get_description(self):
        return "Price, market cap and volume"

    def market_btc(self):
        self.data_btc = Market().ticker(self.coin_id, convert="BTC")

    def market_eur(self):
        self.data_eur = Market().ticker(self.coin_id, convert="EUR")
